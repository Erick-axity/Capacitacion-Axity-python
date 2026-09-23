from dataclasses import dataclass
from typing import Dict, Optional, Protocol

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field


# =====================================================================
# CAPA 1: DOMINIO (El núcleo). ¡No importa nada de afuera!
# =====================================================================
@dataclass
class OrderEntity:
    """ENTIDAD: Reglas de negocio puras."""

    id: str
    producto: str
    cantidad: int

    def es_valida(self) -> bool:
        return self.cantidad > 0


# LOS PUERTOS (Interfaces/Protocols). Son las puertas del hexágono.
class OrderRepository(Protocol):
    def guardar(self, order: OrderEntity) -> None: ...
    def buscar(self, id: str) -> Optional[OrderEntity]: ...


class NotificationService(Protocol):
    def notificar(self, mensaje: str) -> None: ...


# =====================================================================
# CAPA 2: APLICACIÓN (Casos de Uso y DTOs)
# =====================================================================
class CreateOrderDTO(BaseModel):
    """DTO (Data Transfer Object): Los datos crudos que entran."""

    id: str
    producto: str
    cantidad: int = Field(..., gt=0)


class CreateOrderUseCase:
    """CASO DE USO: Orquesta la lógica, pero NO sabe si usa SQL o Memoria."""

    def __init__(self, repo: OrderRepository, notifier: NotificationService):
        self.repo = repo
        self.notifier = notifier

    def ejecutar(self, dto: CreateOrderDTO) -> OrderEntity:
        # 1. Convertir DTO a Entidad
        orden = OrderEntity(id=dto.id, producto=dto.producto, cantidad=dto.cantidad)

        # 2. Validar regla de negocio de dominio
        if not orden.es_valida():
            raise ValueError("Orden inválida")

        # 3. Guardar en el puerto
        self.repo.guardar(orden)

        # 4. Notificar en el puerto
        self.notifier.notificar(f"Orden {orden.id} creada para {orden.producto}")

        return orden


# =====================================================================
# CAPA 3: INFRAESTRUCTURA (Los Adaptadores)
# =====================================================================
# Adaptador 1: Base de datos en Memoria
class InMemoryOrderRepo:
    def __init__(self):
        self.db: Dict[str, OrderEntity] = {}

    def guardar(self, order: OrderEntity) -> None:
        self.db[order.id] = order
        print(f"[DB Memoria] Orden {order.id} guardada.")

    def buscar(self, id: str) -> Optional[OrderEntity]:
        return self.db.get(id)


# Adaptador 2: Base de datos SQL (Simulada para el laboratorio)
class SQLAlchemyOrderRepo:
    def guardar(self, order: OrderEntity) -> None:
        print(
            f"[DB SQL] INSERT INTO orders VALUES ('{order.id}', '{order.producto}')..."
        )

    def buscar(self, id: str) -> Optional[OrderEntity]:
        print(f"[DB SQL] SELECT * FROM orders WHERE id='{id}'...")
        return None


# Adaptador 3: Notificador HTTP Simulado
class HttpNotifierAdapter:
    def notificar(self, mensaje: str) -> None:
        print(f"[HTTP Notifier] POST /api/notify -> Payload: {mensaje}")


# =====================================================================
# CAPA 4: FRAMEWORK (FastAPI "Wiring" o Ensamblaje)
# =====================================================================
app = FastAPI(title="Hexagonal API")


# WIRING (Inyección de Dependencias): Aquí decidimos qué adaptadores usar
def get_order_repository() -> OrderRepository:
    # Si quisieras cambiar a SQL, ¡solo cambias esta línea!
    return InMemoryOrderRepo()


def get_notification_service() -> NotificationService:
    return HttpNotifierAdapter()


def get_create_order_usecase(
    repo: OrderRepository = Depends(get_order_repository),
    notifier: NotificationService = Depends(get_notification_service),
) -> CreateOrderUseCase:
    return CreateOrderUseCase(repo=repo, notifier=notifier)


# EL ENDPOINT: FastAPI es solo un "mecanismo de entrega"
@app.post("/api/orders/")
def create_order_endpoint(
    dto: CreateOrderDTO,
    use_case: CreateOrderUseCase = Depends(get_create_order_usecase),
):
    try:
        orden_creada = use_case.ejecutar(dto)
        return {"status": "success", "order_id": orden_creada.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
