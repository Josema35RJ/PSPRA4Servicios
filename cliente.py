import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from colorama import Fore, Style
import pysftp

class SftpClient:
    def __init__(self, hostname='10.10.1.14', port=22):
        self.hostname = hostname
        self.port = port
        self.username = None
        self.password = None
        self.connpiection = None

    def connect(self):
        self.username = input("Introduce tu nombre de usuario: ")
        self.password = input("Introduce tu contraseña: ")

        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None  
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
            root = tk.Tk()
            root.title("Explorador de archivos SFTP")
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()


            x = (screen_width - 600) // 2 
            y = (screen_height - 400) // 2  

            root.geometry(f"600x400+{x}+{y}")

            tree = ttk.Treeview(root)
            tree.pack(side='left', fill='both', expand=True)

            self.insert_files_and_directories(tree, path)

            root.mainloop()
        else:
            print(Fore.RED + "🚫 No estás conectado al servidor." + Style.RESET_ALL)

    def insert_files_and_directories(self, tree, path, parent=''):
        with self.connection.cd(path):  
            for file in self.connection.listdir():
                if file.startswith('.'):  
                    continue
                if self.connection.isdir(file): 
                    id = tree.insert(parent, 'end', text=f"📁 {file}", values=[path])
                    self.insert_files_and_directories(tree, file, id)  
                else:  
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
            root = tk.Tk()
            root.title("Eliminar directorio")
        
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight() 
            
            x = (screen_width - 600) // 2  
            y = (screen_height - 400) // 2  

            root.geometry(f"600x400+{x}+{y}")
            scrollbar = tk.Scrollbar(root)
            scrollbar.pack(side='right', fill='y')

            listbox = tk.Listbox(root, yscrollcommand=scrollbar.set)
            listbox.pack(side='left', fill='both', expand=True)

            for name in self.connection.listdir('.'):  
                if self.connection.isdir(name):
                    listbox.insert(tk.END, name)
       
            listbox.bind('<Double-1>', lambda event: self.remove_directory(listbox.get(listbox.curselection()[0]), root))

            root.mainloop()
        else:
            print(Fore.RED + "🚫 No estás conectado al servidor." + Style.RESET_ALL)

    def remove_directory(self, directory, root):
        result = messagebox.askquestion("Eliminar", f"¿Estás seguro de que quieres eliminar el directorio '{directory}'?", icon='warning')
        if result == 'yes':
            try:
                if len(self.connection.listdir(directory)) > 0:
                    print(Fore.RED + f"🚫 El directorio '{directory}' no está vacío y no puede ser eliminado." + Style.RESET_ALL)
                    return
           
                self.connection.rmdir(directory)
                print(Fore.GREEN + f"📁 Directorio '{directory}' eliminado.")
                root.destroy() 
                self.show_menu()  
            except Exception as e:
                print(Fore.RED + "🚫 Error al eliminar el directorio: " + str(e) + Style.RESET_ALL)
        else:
            print("Operación cancelada.")

    def insert_directories(self, tree, path, parent=''):
        with self.connection.cd(path): 
            files = self.connection.listdir()
            directories = [file for file in files if self.connection.isdir(file)]

            for directory in directories:
                id = tree.insert(parent, 'end', text=f"📁 {directory}", values=[path])
                self.insert_directories(tree, directory, id)


    def upload_file(self):
        root = tk.Tk()

        file_path = filedialog.askopenfilename(parent=root)  
        root.destroy()  
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
            root = tk.Tk()
            root.title("Descargar archivo")
            
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()

            x = (screen_width - 600) // 2  
            y = (screen_height - 400) // 2  
            root.geometry(f"600x400+{x}+{y}")

            tree = ttk.Treeview(root)
            tree.pack(side='left', fill='both', expand=True)

            self.insert_files(tree, '.')

            tree.bind('<Double-1>', lambda event: self.get_file(tree.item(tree.selection())['values'][0], root))
       
            root.mainloop()
        else:
            print(Fore.RED + "🚫 No estás conectado al servidor." + Style.RESET_ALL)

    def insert_files(self, tree, path):
        for file in self.connection.listdir(path):
            if not file.startswith('.') and not self.connection.isdir(file):  
                tree.insert('', 'end', text=file, values=(path + '/' + file,))

    def get_file(self, path, root):
        if path:  
            download_path = os.path.join(os.path.expanduser('~'), 'Downloads')  
            os.makedirs(download_path, exist_ok=True)  
            if self.connection.isfile(path):  
                if messagebox.askyesno("Confirmación", f"¿Estás seguro de que quieres descargar el archivo '{path}'?", parent=root):
                    self.connection.get(path, os.path.join(download_path, os.path.basename(path)))
                    print(Fore.GREEN + f"⬇️ Archivo '{path}' descargado en la carpeta de descargas.")
                    root.destroy()
            else:
                print(Fore.RED + f"🚫 '{path}' no es un archivo válido en el servidor." + Style.RESET_ALL)
        else:
            print(Fore.RED + "🚫 No se seleccionó ningún archivo." + Style.RESET_ALL)
        
    def delete_file(self):
        if self.connection is not None:
            root = tk.Tk()
            root.title("Eliminar Fichero")
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()

            x = (screen_width - 600) // 2  
            y = (screen_height - 400) // 2  

            root.geometry(f"600x400+{x}+{y}")

            scrollbar = tk.Scrollbar(root)
            scrollbar.pack(side='right', fill='y')

            listbox = tk.Listbox(root, yscrollcommand=scrollbar.set)
            listbox.pack(side='left', fill='both', expand=True)

            for name in self.connection.listdir('.'): 
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
                        root.destroy()  
                        print(Fore.GREEN + f"🗑️  Archivo '{file_to_delete}' eliminado correctamente." + Style.RESET_ALL)
            listbox.bind('<Double-1>', delete_selected_file)

            scrollbar.config(command=listbox.yview)

            root.mainloop()
            
        else:
            print(Fore.RED + "🚫 No estás conectado al servidor." + Style.RESET_ALL)
    
    def finalizar_programa(self):
        print("¡El programa ha finalizado!")
        exit()        
    def show_menu(self):
        options = {
            "1": {"info": "📂 Listar archivos en el servidor", "func": self.list_files},
            "2": {"info": "📁 Crear un directorio en el servidor", "func": self.create_directory},
            "3": {"info": "❌ Eliminar un directorio en el servidor", "func": self.delete_directory},
            "4": {"info": "⬆️  Subir un archivo al servidor", "func": self.upload_file},
            "5": {"info": "⬇️  Descargar un archivo del servidor", "func": self.download_file},
            "6": {"info": "🗑️  Eliminar un archivo del servidor", "func": self.delete_file},
            "7": {"info": "🔌 Desconectar", "func": self.disconnect}
        }

        while True:
            print(Fore.YELLOW + "\n🚀 Bienvenido al cliente SFTP. Aquí están tus opciones:")
            for key, value in options.items():
                print(f"{key}. {value['info']}")

            option = input("\n🔍 Por favor, elige una opción: ")

            if option in options:
                if options[option]["func"] is not None:
                    options[option]
                    if option == "1":
                        self.list_files()
                    elif option == "2":
                        self.create_directory()
                    elif option == "3":
                        self.delete_directory()
                    elif option == "4":
                        self.upload_file()
                    elif option == "5":
                        self.download_file()
                    elif option == "6":
                        self.delete_file()
                    elif option == "7":
                        self.finalizar_programa()
                else:
                    print(Fore.RED + "🚫 Esta opción aún no está implementada." + Style.RESET_ALL)
            else:
                print(Fore.RED + "⚠️ Por favor, elige una opción válida." + Style.RESET_ALL)

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            print(Fore.GREEN + f"🔌 Desconectado del servidor {self.hostname}." + Style.RESET_ALL)

client = SftpClient()
if client.connect():
    client.show_menu()
else:
    print(Fore.RED + "🚫 No se pudo conectar al servidor. Por favor, verifica tus credenciales e intenta de nuevo." + Style.RESET_ALL)
