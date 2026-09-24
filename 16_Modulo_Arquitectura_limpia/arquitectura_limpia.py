from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Protocol

from pydantic import BaseModel


# =====================================================================
# CAPA 1: ENTIDADES Y EVENTOS DE DOMINIO (El núcleo más profundo)
# =====================================================================
@dataclass
class OrderCreated:
    """EVENTO DE DOMINIO: Algo que ya pasó en el sistema."""

    order_id: str
    fecha: datetime = field(default_factory=datetime.now)


@dataclass
class Order:
    """ENTIDAD: Contiene reglas de negocio y registra sus propios eventos."""

    id: str
    producto: str
    cantidad: int
    eventos: List[Any] = field(default_factory=list)

    def crear(self):
        if self.cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a cero")
        # La entidad misma registra que acaba de ser creada
        self.eventos.append(OrderCreated(order_id=self.id))


# =====================================================================
# CAPA 2: CASOS DE USO Y PUERTOS (Reglas de aplicación)
# =====================================================================
# 2A. Los DTOs (Request / Response)
class CreateOrderRequest(BaseModel):
    id: str
    producto: str
    cantidad: int


class OrderViewModel(BaseModel):
    """Modelo de vista final que se entregará al usuario (ej. JSON)"""

    mensaje_exito: str
    order_id: str
    fecha_proceso: str


# 2B. Los Puertos (Interfaces)
class OrderRepository(Protocol):
    def guardar(self, order: Order) -> None: ...


class UnitOfWork(Protocol):
    """PATRÓN UoW: Maneja las transacciones de base de datos."""

    orders: OrderRepository

    def __enter__(self) -> "UnitOfWork": ...
    def __exit__(self, exc_type, exc_val, exc_tb) -> None: ...
    def commit(self) -> None: ...


class OrderPresenter(Protocol):
    """PRESENTER: Se encarga de darle un formato bonito a la respuesta."""

    def presentar(self, order: Order) -> OrderViewModel: ...


class MessageBus(Protocol):
    """MESSAGE BUS: Se encarga de avisarle al resto del sistema sobre los eventos."""

    def publicar(self, eventos: List[Any]) -> None: ...


# 2C. El Caso de Uso (Orquestador)
class CreateOrderUseCase:
    def __init__(self, uow: UnitOfWork, bus: MessageBus, presenter: OrderPresenter):
        self.uow = uow
        self.bus = bus
        self.presenter = presenter

    def ejecutar(self, request: CreateOrderRequest) -> OrderViewModel:
        orden = Order(
            id=request.id, producto=request.producto, cantidad=request.cantidad
        )
        orden.crear()  # Ejecuta lógica de dominio y genera el evento

        # 1. TRANSACCIÓN SEGURA CON UoW
        with self.uow:
            self.uow.orders.guardar(orden)
            self.uow.commit()  # Si esto falla, la base de datos hace Rollback

        # 2. PUBLICAR EVENTOS (Ej. Enviar email)
        self.bus.publicar(orden.eventos)
        orden.eventos.clear()  # Limpiamos los eventos ya procesados

        # 3. PRESENTAR LA RESPUESTA
        return self.presenter.presentar(orden)


# =====================================================================
# CAPA 3: INTERFACE ADAPTERS (Controladores, Presenters, Gateways)
# =====================================================================
# Adaptador del Presenter
class ApiOrderPresenter:
    def presentar(self, order: Order) -> OrderViewModel:
        return OrderViewModel(
            mensaje_exito=f"¡Felicidades! Tu orden de {order.producto} fue procesada.",
            order_id=order.id,
            fecha_proceso=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )


# Adaptador del Repositorio (Memoria)
class InMemoryOrderRepo:
    def __init__(self):
        self.db = {}

    def guardar(self, order: Order) -> None:
        self.db[order.id] = order
        print(f"[Repo] Insertando orden {order.id}...")


# Adaptador del Unit of Work
class InMemoryUoW:
    def __init__(self):
        self.orders = InMemoryOrderRepo()
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print("[UoW] Error detectado. Haciendo ROLLBACK...")
        elif not self.committed:
            print("[UoW] No se hizo commit. Haciendo ROLLBACK implícito...")

    def commit(self) -> None:
        self.committed = True
        print("[UoW] Haciendo COMMIT de la transacción en la DB.")


# Adaptador del Message Bus (Manejador de eventos)
class SimpleMessageBus:
    def publicar(self, eventos: List[Any]) -> None:
        for evento in eventos:
            if isinstance(evento, OrderCreated):
                self._manejar_order_created(evento)

    def _manejar_order_created(self, evento: OrderCreated):
        print(
            f"[Bus de Eventos] Enviando EMAIL al cliente por orden {evento.order_id}..."
        )


# =====================================================================
# EJECUCIÓN (Simulando el Controlador Web)
# =====================================================================
if __name__ == "__main__":
    print("--- INICIANDO CLEAN ARCHITECTURE ---")

    # 1. Configurar infraestructura (Wiring)
    uow = InMemoryUoW()
    bus = SimpleMessageBus()
    presenter = ApiOrderPresenter()

    # 2. Inyectar dependencias al Caso de Uso
    use_case = CreateOrderUseCase(uow=uow, bus=bus, presenter=presenter)

    # 3. Petición HTTP falsa (Controller)
    request_data = CreateOrderRequest(id="A1", producto="Monitor", cantidad=2)

    # 4. Ejecutar Caso de Uso
    respuesta_json = use_case.ejecutar(request_data)

    print("\n--- RESPUESTA PARA EL CLIENTE HTTP ---")
    print(respuesta_json.model_dump_json(indent=2))
