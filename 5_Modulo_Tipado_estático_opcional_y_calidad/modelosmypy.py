from dataclasses import dataclass, field
from typing import Any, Dict, Literal, Union

from pydantic import BaseModel, Field, ValidationError

# =====================================================================
# 1. OBJETIVOS DEL MÓDULO: Union y Literal aplicados
# =====================================================================
# LITERAL: El estado solo puede ser una de estas dos palabras exactas
EstadoOrden = Literal["Procesado", "Rechazado", "Pendiente"]

# UNION: El ID de la orden podría llegar como entero (1) o como texto ("1")
IdOrden = Union[int, str]


# =====================================================================
# 2. TIPADO EN DATACLASSES
# =====================================================================
@dataclass
class Order:
    id: int
    cliente: str
    precio_unitario: float
    cantidad: int
    total: float = field(init=False)

    def __post_init__(self) -> None:  # Tipo de retorno explícito: None
        self.total = self.precio_unitario * self.cantidad

    # Tipamos el parámetro 'otra_orden' esperando cualquier objeto (Any) o Order.
    # El retorno de las comparaciones mágicas siempre es un booleano (bool)
    def __lt__(self, otra_orden: Any) -> bool:
        if not isinstance(otra_orden, Order):
            return NotImplemented
        return self.total < otra_orden.total

    def __eq__(self, otra_orden: Any) -> bool:
        if not isinstance(otra_orden, Order):
            return NotImplemented
        return self.id == otra_orden.id


# =====================================================================
# 3. TIPADO EN MODELOS PYDANTIC
# =====================================================================
class OrderIn(BaseModel):
    # Aquí usamos la Union 'IdOrden' (int o str)
    id: IdOrden = Field(..., description="Puede ser entero o texto")
    cliente: str = Field(..., min_length=3)
    precio_unitario: float = Field(..., gt=0.0)
    cantidad: int = Field(..., gt=0, le=100)


class OrderOut(BaseModel):
    order_id: int
    nombre_cliente: str
    monto_final: float
    # Usamos el Literal definido arriba
    estado: EstadoOrden = "Procesado"


# =====================================================================
# 4. TIPADO EN FUNCIONES (Dict y Str)
# =====================================================================
# Dict[str, Any] significa: "Un diccionario cuyas llaves son texto y sus valores son cualquier cosa"
def procesar_orden(datos_crudos: Dict[str, Any]) -> str:
    print(f"\n Recibiendo datos: {datos_crudos}")
    try:
        orden_valida: OrderIn = OrderIn(**datos_crudos)  # Anotación de variable

        # Pydantic convierte automáticamente el ID a entero (coerción)
        # si se lo enviamos como texto, gracias al tipado.
        id_validado: int = int(orden_valida.id)

        entidad_orden: Order = Order(
            id=id_validado,
            cliente=orden_valida.cliente,
            precio_unitario=orden_valida.precio_unitario,
            cantidad=orden_valida.cantidad,
        )

        orden_salida: OrderOut = OrderOut(
            order_id=entidad_orden.id,
            nombre_cliente=entidad_orden.cliente,
            monto_final=entidad_orden.total,
            estado="Procesado",  # Debe coincidir con el Literal 'EstadoOrden'
        )

        return orden_salida.model_dump_json()

    except ValidationError as e:
        print(f" Pydantic: Error de validación detectado:\n{e.json()}")
        # Devolvemos un JSON válido como String en caso de error
        return '{"estado": "Rechazado", "error": "Datos inválidos"}'


# =====================================================================
# EJECUCIÓN
# =====================================================================
if __name__ == "__main__":
    # Prueba 1: ID numérico
    datos_buenos: Dict[str, Any] = {
        "id": 1,
        "cliente": "Empresa ACME",
        "precio_unitario": 50.5,
        "cantidad": 4,
    }
    json_salida: str = procesar_orden(datos_buenos)

    # Prueba 2: Probando la UNION (enviando el ID como String en lugar de Int)
    datos_string: Dict[str, Any] = {
        "id": "99",
        "cliente": "Stark Ind",
        "precio_unitario": 200.0,
        "cantidad": 2,
    }
    json_salida2: str = procesar_orden(datos_string)
