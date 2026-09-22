from dataclasses import dataclass
from typing import List, Protocol


# =====================================================================
# 1. ENTIDAD DE DOMINIO (El núcleo)
# =====================================================================
@dataclass
class Usuario:
    id: int
    nombre: str


# =====================================================================
# 2. EL PUERTO (Inversión de Dependencias - DIP / Segregación - ISP)
# =====================================================================
class RepositorioUsuarios(Protocol):
    """
    EL CONTRATO: Cualquier clase que quiera ser un Repositorio,
    DEBE implementar estos métodos exactos. (Duck Typing).
    """

    def guardar(self, usuario: Usuario) -> None: ...

    def obtener_todos(self) -> List[Usuario]: ...


# =====================================================================
# 3. EL SERVICIO (Single Responsibility - SRP)
# =====================================================================
class ServicioRegistro:
    """
    La lógica de negocio. NO sabe nada de SQL, ni de Memoria.
    Solo sabe que existe "algo" que cumple el contrato RepositorioUsuarios.
    """

    def __init__(self, repositorio: RepositorioUsuarios):
        # Inyección de Dependencias
        self.repo = repositorio

    def registrar_usuario(self, id: int, nombre: str) -> None:
        if len(nombre) < 3:
            raise ValueError("El nombre es muy corto")
        nuevo_usuario = Usuario(id=id, nombre=nombre)
        self.repo.guardar(nuevo_usuario)
        print(f"Servicio: Lógica de negocio completada para {nombre}")


# =====================================================================
# 4. LOS ADAPTADORES (Open/Closed - OCP y Sustitución de Liskov - LSP)
# =====================================================================
# Adaptador 1: Para pruebas o desarrollo rápido
class RepositorioEnMemoria:
    def __init__(self):
        self._db: List[Usuario] = []

    def guardar(self, usuario: Usuario) -> None:
        self._db.append(usuario)
        print(f"Memoria: Usuario {usuario.nombre} guardado en RAM.")

    def obtener_todos(self) -> List[Usuario]:
        return self._db


# Adaptador 2: Para Producción
class RepositorioSQL:
    def guardar(self, usuario: Usuario) -> None:
        print(
            f"SQL: Ejecutando INSERT INTO users VALUES ({usuario.id}, '{usuario.nombre}')."
        )

    def obtener_todos(self) -> List[Usuario]:
        print("SQL: Ejecutando SELECT * FROM users.")
        return []


# =====================================================================
# EJECUCIÓN DEL LABORATORIO
# =====================================================================
if __name__ == "__main__":
    print("--- INICIANDO CON REPOSITORIO EN MEMORIA (TESTING) ---")
    repo_test = RepositorioEnMemoria()
    servicio_test = ServicioRegistro(repositorio=repo_test)
    servicio_test.registrar_usuario(1, "Ana")

    print("\n--- INICIANDO CON REPOSITORIO SQL (PRODUCCIÓN) ---")
    # FACTORY PATTERN BÁSICO:
    # Cambiamos la base de datos sin tocar ni una línea del ServicioRegistro.
    repo_prod = RepositorioSQL()
    servicio_prod = ServicioRegistro(repositorio=repo_prod)
    servicio_prod.registrar_usuario(2, "Carlos")
