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

    def list_files(self, path='.'):
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
            self.insert_files(tree, path)

            # Muestra la ventana
            root.mainloop()
        else:
            print(Fore.RED + "🚫 No estás conectado al servidor." + Style.RESET_ALL)

    def insert_files(self, tree, path, parent=''):
        with self.connection.cd(path):  # Cambia al directorio que quieras
            files = self.connection.listdir()
            directories = [file for file in files if self.connection.isdir(file)]
            files = [file for file in files if file not in directories]

            for directory in directories:
                id = tree.insert(parent, 'end', text=f"📁 {directory}", values=[path])
                self.insert_files(tree, directory, id)

            for file in files:
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

            # Crea un Treeview con barras de desplazamiento
            tree = ttk.Treeview(root)
            tree.pack(side='left', fill='both', expand=True)

            # Añade los directorios al Treeview
            self.insert_directories(tree, '.')

            # Añade un evento de doble clic para eliminar directorios
            tree.bind('<Double-1>', lambda e: self.remove_directory(tree.item(tree.selection())['values'][0]))

            # Muestra la ventana
            root.mainloop()
        else:
            print(Fore.RED + "🚫 No estás conectado al servidor." + Style.RESET_ALL)

    def insert_directories(self, tree, path, parent=''):
        with self.connection.cd(path):  # Cambia al directorio que quieras
            files = self.connection.listdir()
            directories = [file for file in files if self.connection.isdir(file)]

            for directory in directories:
                id = tree.insert(parent, 'end', text=f"📁 {directory}", values=[path])
                self.insert_directories(tree, directory, id)

    def remove_directory(self, path):
        result = messagebox.askquestion("Eliminar", f"¿Estás seguro de que quieres eliminar el directorio '{path}'?", icon='warning')
        if result == 'yes':
            self.connection.rmdir(path)
            print(Fore.GREEN + f"📁 Directorio '{path}' eliminado.")
        else:
            print("Operación cancelada.")

    def upload_file(self):
        if self.connection is not None:
            # Crea una nueva ventana de Tkinter
            root = tk.Tk()
            root.title("Subir archivo")

            # Crea un Treeview con barras de desplazamiento
            tree = ttk.Treeview(root)
            tree.pack(side='left', fill='both', expand=True)

            # Añade los archivos al Treeview
            self.insert_files(tree, '.')

            # Crea un botón "Subir"
            upload_button = tk.Button(root, text="Subir", command=lambda: self.put_file(tree.item(tree.selection())['values'][0]))
            upload_button.pack(side='right')

            # Muestra la ventana
            root.mainloop()
        else:
            print(Fore.RED + "🚫 No estás conectado al servidor." + Style.RESET_ALL)

    def put_file(self, path):
        self.connection.put(path)
        print(Fore.GREEN + f"⬆️ Archivo '{path}' subido.")

    def download_file(self):
        if self.connection is not None:
            # Crea una nueva ventana de Tkinter
            root = tk.Tk()
            root.title("Descargar archivo")

            # Crea un Treeview con barras de desplazamiento
            tree = ttk.Treeview(root)
            tree.pack(side='left', fill='both', expand=True)

            # Añade los archivos al Treeview
            self.insert_files(tree, '.')

            # Crea un botón "Descargar"
            download_button = tk.Button(root, text="Descargar", command=lambda: self.get_file(tree.item(tree.selection())['values'][0]))
            download_button.pack(side='right')

            # Muestra la ventana
            root.mainloop()
        else:
            print(Fore.RED + "🚫 No estás conectado al servidor." + Style.RESET_ALL)

    def get_file(self, path):
        self.connection.get(path)
        print(Fore.GREEN + f"⬇️ Archivo '{path}' descargado.")

    def delete_file(self):
        file_name = input("Introduce el nombre del archivo que quieres eliminar: ")
        if self.connection is not None:
            self.connection.remove(file_name)
            print(Fore.GREEN + f"🗑️ Archivo '{file_name}' eliminado.")
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
