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
            print(Fore.GREEN + f"Conectado a {self.hostname} como {self.username}." + Style.RESET_ALL)
            return True
        except Exception as err:
            print(Fore.RED + f"No se pudo conectar al servidor: {err}" + Style.RESET_ALL)
            return False

    def list_files(self):
        if self.connection is not None:
            with self.connection.cd('.'):  # Cambia al directorio que quieras
                files = self.connection.listdir()
                for file in files:
                    print(file)

    def create_directory(self):
        directory_name = input("Introduce el nombre del directorio que quieres crear: ")
        if self.connection is not None:
            self.connection.mkdir(directory_name)
            print(f"Directorio '{directory_name}' creado.")

    def delete_directory(self):
        directory_name = input("Introduce el nombre del directorio que quieres eliminar: ")
        if self.connection is not None:
            self.connection.rmdir(directory_name)
            print(f"Directorio '{directory_name}' eliminado.")

    def upload_file(self):
        file_name = input("Introduce el nombre del archivo que quieres subir: ")
        if self.connection is not None:
            self.connection.put(file_name)
            print(f"Archivo '{file_name}' subido.")

    def download_file(self):
        file_name = input("Introduce el nombre del archivo que quieres descargar: ")
        if self.connection is not None:
            self.connection.get(file_name)
            print(f"Archivo '{file_name}' descargado.")

    def delete_file(self):
        file_name = input("Introduce el nombre del archivo que quieres eliminar: ")
        if self.connection is not None:
            self.connection.remove(file_name)
            print(f"Archivo '{file_name}' eliminado.")

    def show_menu(self):
        options = {
            "1": {"info": "📂 Listar archivos en el servidor", "func": self.list_files},
            "2": {"info": "📁 Crear un directorio en el servidor", "func": self.create_directory},
            "3": {"info": "❌ Eliminar un directorio en el servidor", "func": self.delete_directory},
            "4": {"info": "⬆️ Subir un archivo al servidor", "func": self.upload_file},
            "5": {"info": "⬇️ Descargar un archivo del servidor", "func": self.download_file},
            "6": {"info": "🗑️ Eliminar un archivo del servidor", "func": self.delete_file},
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
                    if option == "7":
                        break
                else:
                    print(Fore.RED + "🚫 Esta opción aún no está implementada." + Style.RESET_ALL)
            else:
                print(Fore.RED + "⚠️ Por favor, elige una opción válida." + Style.RESET_ALL)

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            print(Fore.GREEN + f"Desconectado del servidor {self.hostname}." + Style.RESET_ALL)

# Crea una instancia del cliente Sftp y conéctate al servidor
client = SftpClient()
if client.connect():
    # Muestra el menú solo si la conexión fue exitosa
    client.show_menu()
else:
    print(Fore.RED + "No se pudo conectar al servidor. Por favor, verifica tus credenciales e intenta de nuevo." + Style.RESET_ALL)
