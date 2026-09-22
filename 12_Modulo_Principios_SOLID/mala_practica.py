# MALA PRÁCTICA: Rompe OCP, DIP y SRP
class BaseDeDatosSQL:
    def guardar_usuario(self, nombre: str):
        print(f"INSERT INTO users VALUES ('{nombre}')")


class RegistroDeUsuarios:
    def __init__(self):
        # ❌ Alto Acoplamiento: El servicio depende directamente de SQL
        self.db = BaseDeDatosSQL()

    def registrar(self, nombre: str):
        # Lógica de negocio mezclada con detalles técnicos
        if len(nombre) > 2:
            self.db.guardar_usuario(nombre)
