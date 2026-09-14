import random
import time


# =====================================================================
# 1. CONTEXT MANAGER: Temporización (Uso de 'with')
# =====================================================================
class Temporizador:
    """Mide automáticamente cuánto tiempo tarda en ejecutarse un bloque de código."""

    def __enter__(self):
        self.inicio = time.time()
        return self  # Aquí entramos al bloque 'with'

    def __exit__(self, exc_type, exc_val, exc_tb):
        tiempo_total = time.time() - self.inicio
        print(
            f"\n [Temporizador] Tiempo total de ejecución: {tiempo_total:.2f} segundos"
        )
        # Si hubiera un error, exc_type tendría información, pero dejamos que fluya.


# =====================================================================
# 2. DECORADOR Y CLOSURES: Reintentos con Backoff
# =====================================================================
def reintentar_con_backoff(max_reintentos=3, delay_inicial=1):
    """
    Decorador que reintenta una función si falla.
    'Backoff' significa que cada vez que falla, espera el doble de tiempo (1s, 2s, 4s...).
    """

    def decorador(func):
        def wrapper(
            *args, **kwargs
        ):  # Uso de argumentos dinámicos posicionales y nombrados
            delay = delay_inicial
            for intento in range(1, max_reintentos + 1):
                try:
                    return func(*args, **kwargs)  # Ejecuta la función original
                except Exception as e:
                    print(f"  [⚠️ Error] Intento {intento}/{max_reintentos} falló: {e}")
                    if intento == max_reintentos:
                        print(" Límite de reintentos alcanzado. Abortando.")
                        raise e  # Si es el último intento, lanza el error

                    print(f" Esperando {delay} segundos para el próximo intento...")
                    time.sleep(delay)
                    delay *= 2  # Backoff exponencial (multiplica el tiempo de espera)

        return wrapper

    return decorador


# =====================================================================
# 3. GENERADOR: Lotes de datos (Uso de 'yield')
# =====================================================================
def generador_lotes(iterable, tamaño_lote):
    """Toma una lista grande y genera pequeños lotes uno por uno."""
    for i in range(0, len(iterable), tamaño_lote):
        # 'yield' pausa la función y entrega el dato sin cargar todo en memoria a la vez
        yield iterable[i : i + tamaño_lote]


# =====================================================================
# APLICACIÓN: Diseño de API clara combinando todo
# =====================================================================


# Usamos el decorador que creamos arriba.
# El asterisco (*) fuerza a que 'destino' se pase siempre con su nombre (Keyword argument)
@reintentar_con_backoff(max_reintentos=3, delay_inicial=1)
def enviar_datos_api(lote, *, destino="Servidor"):
    """Simula el envío de datos con una probabilidad del 40% de fallo."""
    print(f"Enviando {lote} a {destino}...")

    if random.random() < 0.40:  # 40% de probabilidad de que falle la red simulada
        raise ConnectionError("Se perdió la conexión con el servidor")

    print(" Lote enviado con éxito.")
    return True


# =====================================================================
# EJECUCIÓN PRINCIPAL
# =====================================================================
if __name__ == "__main__":
    # Comprensión de listas: Crea una lista del 1 al 10 en una sola línea
    datos_completos = [x for x in range(1, 56)]

    print("Iniciando procesamiento de datos...")

    # Context Manager: Se asegura de iniciar y detener el cronómetro automáticamente
    with Temporizador():

        # Iterador/Generador: Pedimos lotes de 3 en 3
        for lote_actual in generador_lotes(datos_completos, tamaño_lote=10):
            print("-" * 30)
            try:
                enviar_datos_api(lote_actual, destino="Base de Datos Central")
            except ConnectionError:
                print(
                    f"Saltando el lote {lote_actual} debido a fallos de red continuos."
                )
