import time

from patrones import (
    AdaptadorStripeLegacy,
    CalculadoraCheckout,
    DescuentoLiquidacion,
    DescuentoVIP,
    PrecioNormal,
    obtener_tasa_cambio,
)


def test_decorator_cache():
    """Prueba que el decorador evite la lentitud en la segunda llamada."""
    # Primera llamada (debe tardar ~1 segundo)
    inicio = time.time()
    res1 = obtener_tasa_cambio("MXN")
    tiempo1 = time.time() - inicio

    # Segunda llamada (debe ser instantánea gracias al caché)
    inicio = time.time()
    res2 = obtener_tasa_cambio("MXN")
    tiempo2 = time.time() - inicio

    assert res1 == 17.50
    assert res2 == 17.50
    assert tiempo1 >= 1.0  # El primero es lento
    assert tiempo2 < 0.1  # El segundo es casi 0 segundos


def test_strategy_precios():
    """Prueba que el Checkout calcule distinto según la estrategia inyectada."""
    monto_base = 100.0

    checkout_normal = CalculadoraCheckout(PrecioNormal())
    assert checkout_normal.procesar(monto_base) == 100.0

    checkout_vip = CalculadoraCheckout(DescuentoVIP())
    assert checkout_vip.procesar(monto_base) == 80.0

    checkout_liq = CalculadoraCheckout(DescuentoLiquidacion())
    assert checkout_liq.procesar(monto_base) == 50.0


def test_adapter_proveedor_externo():
    """Prueba que el Adaptador traduzca correctamente los tipos de datos."""
    proveedor = AdaptadorStripeLegacy()

    # Usamos nuestra interfaz moderna (enviamos un float, recibimos un bool)
    resultado = proveedor.pagar(150.50)

    assert resultado is True
