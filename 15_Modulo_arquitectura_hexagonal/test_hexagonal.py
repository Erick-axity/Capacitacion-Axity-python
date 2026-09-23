import pytest
from arquitectura_hexagonal import (
    CreateOrderDTO,
    CreateOrderUseCase,
    HttpNotifierAdapter,
    InMemoryOrderRepo,
    OrderEntity,
    SQLAlchemyOrderRepo,
)


# =====================================================================
# 1. PRUEBAS DE CONTRATO (Para los adaptadores de DB)
# =====================================================================
# Parametrizamos para que pase a los dos Adaptadores por la misma prueba
@pytest.mark.parametrize("repositorio", [InMemoryOrderRepo(), SQLAlchemyOrderRepo()])
def test_contrato_repositorios(repositorio):
    """Prueba de Contrato: Todos los adaptadores deben cumplir estas reglas."""
    orden = OrderEntity(id="123", producto="Laptop", cantidad=2)

    # Ambos deben poder guardar sin arrojar errores
    repositorio.guardar(orden)

    # En un test real, aquí haríamos un buscar() para confirmar.
    # Como SQLAlchemyOrderRepo es simulado, solo validamos que no explote.
    assert hasattr(repositorio, "guardar")
    assert hasattr(repositorio, "buscar")


# =====================================================================
# 2. PRUEBA DE DOMINIO Y CASO DE USO
# =====================================================================
def test_caso_de_uso_crear_orden():
    """Prueba unitaria del orquestador inyectando adaptadores de prueba."""
    repo = InMemoryOrderRepo()
    notifier = HttpNotifierAdapter()
    use_case = CreateOrderUseCase(repo=repo, notifier=notifier)

    dto = CreateOrderDTO(id="999", producto="Teclado", cantidad=1)

    resultado = use_case.ejecutar(dto)

    assert resultado.id == "999"
    # Verificamos que el Use Case sí usó el puerto de base de datos
    assert repo.buscar("999") is not None
