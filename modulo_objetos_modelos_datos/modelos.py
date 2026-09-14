from dataclasses import dataclass, field

from pydantic import BaseModel, Field, ValidationError


# =====================================================================
# 1. ENTIDAD DE DOMINIO: Dataclass, Cálculos Derivados y Dunder Methods
# =====================================================================
@dataclass
class Order:
    """Modelo de datos interno (Entidad de negocio pura)."""

    id: int
    cliente: str
    precio_unitario: float
    cantidad: int
    # El campo 'total' no se pide al crear el objeto, se calcula solo
    total: float = field(init=False)

    def __post_init__(self):
        # CÁLCULO DERIVADO: Se ejecuta automáticamente después de instanciar
        self.total = self.precio_unitario * self.cantidad

    # DUNDER METHODS: Para permitir comparaciones (>, <, ==) entre órdenes
    def __lt__(self, otra_orden):
        """Permite usar el símbolo '<' para comparar qué orden es más barata."""
        if not isinstance(otra_orden, Order):
            return NotImplemented
        return self.total < otra_orden.total

    def __eq__(self, otra_orden):
        """Permite usar '==' para saber si dos órdenes son exactamente la misma (por ID)."""
        if not isinstance(otra_orden, Order):
            return NotImplemented
        return self.id == otra_orden.id


# =====================================================================
# 2. MODELOS PYDANTIC: Validación (Entrada) y Serialización (Salida)
# =====================================================================
class OrderIn(BaseModel):
    """Modelo para VALIDAR los datos crudos que entran a nuestro sistema."""

    id: int = Field(..., gt=0, description="El ID debe ser mayor a 0")
    cliente: str = Field(..., min_length=3, description="Mínimo 3 caracteres")
    precio_unitario: float = Field(..., gt=0.0)
    cantidad: int = Field(..., gt=0, le=100)  # Máximo 100 artículos por orden


class OrderOut(BaseModel):
    """Modelo para SERIALIZAR (dar formato) a los datos que salen de nuestro sistema."""

    order_id: int
    nombre_cliente: str
    monto_final: float
    estado: str = "Procesado"  # Valor por defecto agregado en la salida


# =====================================================================
# 3. CONVERSIÓN: Pydantic -> Dataclass -> Pydantic
# =====================================================================
def procesar_orden(datos_crudos: dict) -> str:
    print(f"\n Recibiendo datos: {datos_crudos}")
    try:
        # 1. VALIDACIÓN (Pydantic OrderIn)
        orden_valida = OrderIn(**datos_crudos)
        print(" Pydantic: Datos de entrada validados correctamente.")

        # 2. CONVERSIÓN A ENTIDAD (Dataclass Order)
        entidad_orden = Order(
            id=orden_valida.id,
            cliente=orden_valida.cliente,
            precio_unitario=orden_valida.precio_unitario,
            cantidad=orden_valida.cantidad,
        )
        print(
            f" Dataclass: Entidad creada. Total calculado automáticamente: ${entidad_orden.total}"
        )

        # 3. SERIALIZACIÓN (Pydantic OrderOut)
        orden_salida = OrderOut(
            order_id=entidad_orden.id,
            nombre_cliente=entidad_orden.cliente,
            monto_final=entidad_orden.total,
        )
        print(" Pydantic: Objeto serializado para salida.")

        # Devolvemos un JSON listo para enviar por una API
        return orden_salida.model_dump_json()

    except ValidationError as e:
        print(f" Pydantic: Error de validación detectado:\n{e.json()}")
        return '{"error": "Datos inválidos"}'


# =====================================================================
# EJECUCIÓN DEL LABORATORIO
# =====================================================================
if __name__ == "__main__":
    # Prueba 1: Datos correctos
    datos_buenos = {
        "id": 1,
        "cliente": "Empresa ACME",
        "precio_unitario": 50.5,
        "cantidad": 4,
    }
    json_salida = procesar_orden(datos_buenos)
    print(f"JSON Final: {json_salida}")

    # Prueba 2: Datos incorrectos (Cantidad excede el límite y cliente muy corto)
    datos_malos = {"id": 2, "cliente": "A", "precio_unitario": 10.0, "cantidad": 500}
    procesar_orden(datos_malos)

    # Prueba 3: Probando las comparaciones (Dunder Methods en el Dataclass)
    print("\n Probando comparaciones (Dunder Methods):")
    orden1 = Order(id=1, cliente="A", precio_unitario=100, cantidad=1)  # Total 100
    orden2 = Order(id=2, cliente="B", precio_unitario=60, cantidad=2)  # Total 120

    print(f"¿Orden 1 es más barata que Orden 2? {'Sí' if orden1 < orden2 else 'No'}")
