import pysftp

class Sftp:
    def __init__(self, hostname='localhost', username='username', password='password', port=22):
        """Constructor Method"""
        self.connection = None
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port

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
            print(f"Conectado a {self.hostname} como {self.username}.")
        except Exception as err:
            print(f"No se pudo conectar al servidor: {err}")

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            print(f"Desconectado del servidor {self.hostname}")

# Crear una instancia de la clase Sftp
sftp = Sftp()
sftp.connect()
