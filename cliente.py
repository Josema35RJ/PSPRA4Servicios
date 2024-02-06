import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from colorama import Fore, Style
import pysftp

class SftpClient:
    def __init__(self, hostname='10.10.1.14', username='anakin', password='skywalker', port=22):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.connection = None

    def connect(self):
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None  # Desactiva la comprobación de HostKey
        try:
            self.connection = pysftp.Connection(
                host=self.hostname,
                username=self.username,
                password=self.password,
                port=self.port,
                cnopts=cnopts
            )
            print(Fore.GREEN + f"🔌 Conectado a {self.hostname} como {self.username}." + Style.RESET_ALL)
            return True
        except Exception as err:
            print(Fore.RED + f"🚫 No se pudo conectar al servidor: {err}" + Style.RESET_ALL)
            return False

    def list_files(self, path='/home/anakin'):
        if self.connection is not None:
            # Crea una nueva ventana de Tkinter
            root = tk.Tk()
            root.title("Explorador de archivos SFTP")
            # Obtener las dimensiones de la pantalla
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()

            # Calcular las coordenadas para centrar la ventana
            x = (screen_width - 600) // 2  # 600 es el ancho de la ventana
            y = (screen_height - 400) // 2  # 400 es el alto de la ventana

            # Establecer la geometría para centrar la ventana
            root.geometry(f"600x400+{x}+{y}")

            # Crea un Treeview con barras de desplazamiento
            tree = ttk.Treeview(root)
            tree.pack(side='left', fill='both', expand=True)

            # Añade los directorios y archivos al Treeview
            self.insert_files_and_directories(tree, path)

            # Muestra la ventana
            root.mainloop()
        else:
            print(Fore.RED + "🚫 No estás conectado al servidor." + Style.RESET_ALL)

    def insert_files_and_directories(self, tree, path, parent=''):
        with self.connection.cd(path):  # Cambia al directorio que quieras
            for file in self.connection.listdir():
                if file.startswith('.'):  # Ignora los archivos y directorios privados
                    continue
                if self.connection.isdir(file):  # Si es un directorio
                    id = tree.insert(parent, 'end', text=f"📁 {file}", values=[path])
                    self.insert_files_and_directories(tree, file, id)  # Recursivamente inserta los archivos/directorios dentro
                else:  # Si es un archivo
                    tree.insert(parent, 'end', text=f"📄 {file}", values=[path])

    def create_directory(self):
        directory_name = input("Introduce el nombre del directorio que quieres crear: ")
        if self.connection is not None:
            self.connection.mkdir(directory_name)
            print(Fore.GREEN + f"📁 Directorio '{directory_name}' creado.")
        else:
            print(Fore.RED + "🚫 No estás conectado al servidor." + Style.RESET_ALL)

    def delete_directory(self):
        if self.connection is not None:
            # Crea una nueva ventana de Tkinter
            root = tk.Tk()
            root.title("Eliminar directorio")
           
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight() # Calcular las coordenadas para centrar la ventana
            
            x = (screen_width - 600) // 2  # 600 es el ancho de la ventana
            y = (screen_height - 400) // 2  # 400 es el alto de la ventana

                # Establecer la geometría para centrar la ventana
            root.geometry(f"600x400+{x}+{y}")
            # Crea una lista con barras de desplazamiento
            scrollbar = tk.Scrollbar(root)
            scrollbar.pack(side='right', fill='y')

            listbox = tk.Listbox(root, yscrollcommand=scrollbar.set)
            listbox.pack(side='left', fill='both', expand=True)

            # Añade solo los directorios del servidor a la lista
            for name in self.connection.listdir('.'):  # '.' representa el directorio actual en el servidor
                if self.connection.isdir(name):
                    listbox.insert(tk.END, name)

            # Elimina el directorio al hacer doble clic en él
            listbox.bind('<Double-1>', lambda event: self.remove_directory(listbox.get(listbox.curselection()[0]), root))

            # Muestra la ventana
            root.mainloop()
        else:
            print(Fore.RED + "🚫 No estás conectado al servidor." + Style.RESET_ALL)

    def remove_directory(self, directory, root):
        result = messagebox.askquestion("Eliminar", f"¿Estás seguro de que quieres eliminar el directorio '{directory}'?", icon='warning')
        if result == 'yes':
            try:
                # Comprueba si el directorio está vacío
                if len(self.connection.listdir(directory)) > 0:
                    print(Fore.RED + f"🚫 El directorio '{directory}' no está vacío y no puede ser eliminado." + Style.RESET_ALL)
                    return

                # Ahora elimina el directorio
                self.connection.rmdir(directory)
                print(Fore.GREEN + f"📁 Directorio '{directory}' eliminado.")
                root.destroy()  # Cierra la ventana actual
                self.delete_directory()  # Abre una nueva ventana con la lista actualizada de directorios
            except Exception as e:
                print(Fore.RED + "🚫 Error al eliminar el directorio: " + str(e) + Style.RESET_ALL)
        else:
            print("Operación cancelada.")

    def insert_directories(self, tree, path, parent=''):
        with self.connection.cd(path):  # Cambia al directorio que quieras
            files = self.connection.listdir()
            directories = [file for file in files if self.connection.isdir(file)]

            for directory in directories:
                id = tree.insert(parent, 'end', text=f"📁 {directory}", values=[path])
                self.insert_directories(tree, directory, id)


    def upload_file(self):
        root = tk.Tk()

        file_path = filedialog.askopenfilename(parent=root)  # Abre el explorador de archivos y permite al usuario seleccionar un archivo
        root.destroy()  # Cierra la ventana principal de tkinter
        if file_path:
            if self.connection is not None:
                try:
                    self.connection.put(file_path)
                    print(f"Archivo '{file_path}' subido.")
                except Exception as e:
                    print(f"Error al subir el archivo: {e}")
            else:
                print("No estás conectado al servidor.")
        else:
            print("No se seleccionó ningún archivo.")

    def put_file(self, path):
        self.connection.put(path)
        print(Fore.GREEN + f"⬆️ Archivo '{path}' subido.")

    def download_file(self):
        if self.connection is not None:
            # Crea una nueva ventana de Tkinter
            root = tk.Tk()
            root.title("Descargar archivo")
            
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()

                # Calcular las coordenadas para centrar la ventana
            x = (screen_width - 600) // 2  # 600 es el ancho de la ventana
            y = (screen_height - 400) // 2  # 400 es el alto de la ventana
                # Establecer la geometría para centrar la ventana
            root.geometry(f"600x400+{x}+{y}")

            # Crea un Treeview con barras de desplazamiento
            tree = ttk.Treeview(root)
            tree.pack(side='left', fill='both', expand=True)

            # Añade los archivos al Treeview
            self.insert_files(tree, '.')

            # Vincula la función get_file al evento de doble clic
            tree.bind('<Double-1>', lambda event: self.get_file(tree.item(tree.selection())['values'][0], root))

            # Muestra la ventana
            root.mainloop()
        else:
            print(Fore.RED + "🚫 No estás conectado al servidor." + Style.RESET_ALL)

    def insert_files(self, tree, path):
        for file in self.connection.listdir(path):
            if not file.startswith('.') and not self.connection.isdir(file):  # Excluye los archivos privados y los directorios
                tree.insert('', 'end', text=file, values=(path + '/' + file,))

    def get_file(self, path, root):
        if path:  # Verifica si la ruta del archivo seleccionado es válida
            download_path = os.path.join(os.path.expanduser('~'), 'Downloads')  # Utiliza la carpeta de descargas del usuario
            os.makedirs(download_path, exist_ok=True)  # Crea el directorio si no existe
            if self.connection.isfile(path):  # Verifica si el path es un archivo en el servidor
                # Muestra un mensaje de confirmación antes de descargar el archivo
                if messagebox.askyesno("Confirmación", f"¿Estás seguro de que quieres descargar el archivo '{path}'?", parent=root):
                    self.connection.get(path, os.path.join(download_path, os.path.basename(path)))
                    print(Fore.GREEN + f"⬇️ Archivo '{path}' descargado en la carpeta de descargas.")
            else:
                print(Fore.RED + f"🚫 '{path}' no es un archivo válido en el servidor." + Style.RESET_ALL)
        else:
            print(Fore.RED + "🚫 No se seleccionó ningún archivo." + Style.RESET_ALL)
        
    def delete_file(self):
        if self.connection is not None:
            # Crear una nueva ventana de Tkinter
            root = tk.Tk()
            root.title("Eliminar Fichero")
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()

            x = (screen_width - 600) // 2  # 600 es el ancho de la ventana
            y = (screen_height - 400) // 2  # 400 es el alto de la ventana

            root.geometry(f"600x400+{x}+{y}")

            # Crear una lista con barras de desplazamiento
            scrollbar = tk.Scrollbar(root)
            scrollbar.pack(side='right', fill='y')

            listbox = tk.Listbox(root, yscrollcommand=scrollbar.set)
            listbox.pack(side='left', fill='both', expand=True)

            # Añadir solo los archivos del servidor a la lista
            for name in self.connection.listdir('.'):  # '.' representa el directorio actual en el servidor
                if self.connection.isfile(name) and not name.startswith('.'):
                    listbox.insert(tk.END, name)

            def delete_selected_file(event):
                selected_index = listbox.curselection()
                if selected_index:
                    file_to_delete = listbox.get(selected_index[0])
                    confirmation = messagebox.askyesno("Confirmar", f"¿Estás seguro de que quieres eliminar el fichero '{file_to_delete}'?")
                    if confirmation:
                        self.connection.remove(file_to_delete)
                        listbox.delete(selected_index[0])
                        root.destroy()  # Cerrar la ventana después de eliminar el archivo
                        print(Fore.GREEN + f"🗑️  Archivo '{file_to_delete}' eliminado correctamente." + Style.RESET_ALL)
            # Vincular la función delete_selected_file al evento de doble clic
            listbox.bind('<Double-1>', delete_selected_file)

            # Configurar la barra de desplazamiento para desplazar la lista
            scrollbar.config(command=listbox.yview)

            # Mostrar la ventana
            root.mainloop()
            root.destroy()
        else:
            print(Fore.RED + "🚫 No estás conectado al servidor." + Style.RESET_ALL)
            
    def show_menu(self):
        options = {
            "listar": {"info": "📂 Listar archivos en el servidor", "func": self.list_files},
            "crear": {"info": "📁 Crear un directorio en el servidor", "func": self.create_directory},
            "eliminar": {"info": "❌ Eliminar un directorio en el servidor", "func": self.delete_directory},
            "subir": {"info": "⬆️ Subir un archivo al servidor", "func": self.upload_file},
            "descargar": {"info": "⬇️ Descargar un archivo del servidor", "func": self.download_file},
            "borrar": {"info": "🗑️ Eliminar un archivo del servidor", "func": self.delete_file},
            "desconectar": {"info": "🔌 Desconectar", "func": self.disconnect}
        }

        while True:
            print(Fore.YELLOW + "\n🚀 Bienvenido al cliente SFTP. Aquí están tus opciones:")
            for key, value in options.items():
                print(f"{key}. {value['info']}")

            option = input("\n🔍 Por favor, elige una opción: ")

            if option in options:
                if options[option]["func"] is not None:
                    options[option]
                    if option == "listar":
                        self.list_files()
                    elif option == "crear":
                        self.create_directory()
                    elif option == "eliminar":
                        self.delete_directory()
                    elif option == "subir":
                        self.upload_file()
                    elif option == "descargar":
                        self.download_file()
                    elif option == "borrar":
                        self.delete_file()
                    elif option == "desconectar":
                        break
                else:
                    print(Fore.RED + "🚫 Esta opción aún no está implementada." + Style.RESET_ALL)
            else:
                print(Fore.RED + "⚠️ Por favor, elige una opción válida." + Style.RESET_ALL)

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            print(Fore.GREEN + f"🔌 Desconectado del servidor {self.hostname}." + Style.RESET_ALL)

# Crea una instancia del cliente Sftp y conéctate al servidor
client = SftpClient()
if client.connect():
    # Muestra el menú solo si la conexión fue exitosa
    client.show_menu()
else:
    print(Fore.RED + "🚫 No se pudo conectar al servidor. Por favor, verifica tus credenciales e intenta de nuevo." + Style.RESET_ALL)
