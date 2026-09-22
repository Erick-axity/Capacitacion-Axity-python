import time
from typing import Optional


def consultar_bd_descuento(codigo: str) -> float:
    """Simula una conexión lenta a una base de datos externa."""
    time.sleep(5)  # Simula lentitud
    descuentos = {"VERANO20": 0.20, "MITAD50": 0.50}
    return descuentos.get(codigo, 0.0)


def calcular_precio_final(
    precio_base: float, codigo_promo: Optional[str] = None
) -> float:
    """Calcula el precio final. No puede ser negativo."""
    if precio_base < 0:
        raise ValueError("El precio base no puede ser negativo")

    descuento = 0.0
    if codigo_promo:
        descuento = consultar_bd_descuento(codigo_promo)

    precio_final = precio_base - (precio_base * descuento)
    return max(0.0, precio_final)
