from unittest.mock import patch

import pytest
from calculadora import calcular_precio_final, consultar_bd_descuento
from hypothesis import given
from hypothesis import strategies as st


# =====================================================================
# 1. FIXTURES (Datos reutilizables para tus tests)
# =====================================================================
@pytest.fixture
def precio_estandar():
    """Provee un valor base que muchos tests van a usar."""
    return 100.0


# =====================================================================
# 2. MARKERS (Etiquetar tests)
# =====================================================================
@pytest.mark.fast  # Etiqueta personalizada
def test_precio_sin_descuento(precio_estandar):
    # Uso del fixture 'precio_estandar'
    assert calcular_precio_final(precio_estandar) == 100.0


def test_excepcion_precio_negativo():
    # Verifica que el sistema explote correctamente si mandamos un negativo
    with pytest.raises(ValueError, match="no puede ser negativo"):
        calcular_precio_final(-50.0)


# =====================================================================
# 3. PARAMETRIZACIÓN Y MOCKING (unittest.mock)
# =====================================================================
@pytest.mark.parametrize(
    "codigo, descuento_simulado, esperado",
    [("VERANO20", 0.20, 80.0), ("MITAD50", 0.50, 50.0), ("INVALIDO", 0.0, 100.0)],
)
@patch("calculadora.consultar_bd_descuento")
def test_descuentos_con_mock(
    mock_bd, codigo, descuento_simulado, esperado, precio_estandar
):
    """
    Mock: Evitamos esperar 5 segundos "apagando" la función real de BD
    y obligándola a devolver el 'descuento_simulado'.
    Parametrize: Corre este mismo test 3 veces con datos distintos.
    """
    mock_bd.return_value = descuento_simulado

    resultado = calcular_precio_final(precio_estandar, codigo)
    assert resultado == esperado
    mock_bd.assert_called_once_with(codigo)  # Verifica que sí llamamos a la BD


# =====================================================================
# 4. PROPERTY-BASED TESTING (Hypothesis)
# =====================================================================
@given(
    precio=st.floats(min_value=0.0, max_value=10000.0),
    descuento=st.floats(
        min_value=0.0, max_value=2.0
    ),  # ¿Qué pasa si el descuento es del 200%?
)
@patch("calculadora.consultar_bd_descuento")
def test_propiedades_precio_final(mock_bd, precio, descuento):
    """
    Hypothesis generará 100 escenarios locos con decimales extraños.
    Nosotros no validamos un resultado exacto, validamos las 'propiedades' matemáticas.
    """
    mock_bd.return_value = descuento
    precio_final = calcular_precio_final(precio, "PROMO")

    # PROPIEDAD 1: El precio final NUNCA debe ser negativo
    assert precio_final >= 0.0

    # PROPIEDAD 2: El precio final NUNCA debe ser mayor al precio original
    assert precio_final <= precio


# =====================================================================
# 5. TEST DE INTEGRACIÓN REAL (Para lograr 100% de Coverage)
# =====================================================================
@pytest.mark.slow
def test_funcion_real_base_de_datos():
    """Llama a la función real sin Mock. Tardará 5 segundos."""
    resultado = consultar_bd_descuento("VERANO20")
    assert resultado == 0.20

    # Probando el caso cuando el código no existe
    assert consultar_bd_descuento("INVENTADO") == 0.0
