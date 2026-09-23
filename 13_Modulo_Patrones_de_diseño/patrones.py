import time
from typing import Protocol


# =====================================================================
# 1. PATRÓN IDIOMÁTICO / ESTRUCTURAL: DECORATOR (Caché)
# =====================================================================
def cache_resultados(func):
    """
    Decorador que envuelve a una función para guardar sus resultados.
    Evita recalcular o hacer peticiones repetidas.
    """
    cache = {}

    def wrapper(*args):
        if args in cache:
            print(f"📦 [Caché] Retornando valor guardado para: {args}")
            return cache[args]

        print(f"⚙️ [Caché] Calculando nuevo valor para: {args}")
        resultado = func(*args)
        cache[args] = resultado
        return resultado

    return wrapper


@cache_resultados
def obtener_tasa_cambio(moneda: str) -> float:
    """Simula una llamada muy lenta a una API externa de finanzas."""
    time.sleep(1)  # Simulamos lentitud de red (1 segundo)
    tasas = {"USD": 1.0, "EUR": 0.85, "MXN": 17.50}
    return tasas.get(moneda, 1.0)


# =====================================================================
# 2. PATRÓN COMPORTAMIENTO: STRATEGY (Cálculo de Precios)
# =====================================================================
class EstrategiaPrecio(Protocol):
    """La interfaz (contrato) que todas las estrategias deben cumplir."""

    def calcular(self, monto: float) -> float: ...


class PrecioNormal:
    def calcular(self, monto: float) -> float:
        return monto


class DescuentoVIP:
    def calcular(self, monto: float) -> float:
        return monto * 0.80  # 20% de descuento


class DescuentoLiquidacion:
    def calcular(self, monto: float) -> float:
        return monto * 0.50  # 50% de descuento


class CalculadoraCheckout:
    """El contexto que usa la estrategia. Puede cambiar de estrategia en vivo."""

    def __init__(self, estrategia: EstrategiaPrecio):
        self.estrategia = estrategia

    def procesar(self, monto: float) -> float:
        # Delega el cálculo a la estrategia inyectada
        return self.estrategia.calcular(monto)


# =====================================================================
# 3. PATRÓN ESTRUCTURAL: ADAPTER (Proveedor Externo)
# =====================================================================
# A. La API Externa (Legacy/Terceros). No podemos modificar este código.
class SistemaPagoAntiguoAPI:
    def hacer_cargo_xml(self, total_string: str) -> dict:
        print(f"📡 API Externa: Recibido XML. Procesando cargo de {total_string}")
        return {"status": "SUCCESS", "error_code": None}


# B. Nuestra Interfaz Ideal (Lo que nuestro sistema moderno espera usar)
class ProveedorPago(Protocol):
    def pagar(self, monto: float) -> bool: ...


# C. El Adaptador (El traductor entre lo moderno y lo antiguo)
class AdaptadorStripeLegacy:
    def __init__(self):
        # Instanciamos el sistema viejo por debajo
        self.api_vieja = SistemaPagoAntiguoAPI()

    def pagar(self, monto: float) -> bool:
        # 1. Traduce datos de entrada (De float a string con signo de $)
        monto_str = f"${monto:.2f}"

        # 2. Llama al sistema viejo con el formato que él entiende
        respuesta = self.api_vieja.hacer_cargo_xml(monto_str)

        # 3. Traduce datos de salida (De diccionario a un simple booleano)
        return respuesta.get("status") == "SUCCESS"
