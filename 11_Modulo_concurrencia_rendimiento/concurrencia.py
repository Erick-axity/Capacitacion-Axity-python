import asyncio
import math
import time
from concurrent.futures import ProcessPoolExecutor

import httpx

# =====================================================================
# PARTE 1: I/O BOUND (Operaciones de Red / E/S)
# =====================================================================
URLS = ["https://httpbin.org/delay/1"] * 5  # 5 URLs que tardan 1 seg en responder


# 1A. Versión Síncrona (Lenta - Bloqueante)
def fetch_sincrono():
    print("Iniciando descargas SÍNCRONAS (una por una)...")
    inicio = time.time()
    with httpx.Client() as client:
        for url in URLS:
            client.get(url)
    tiempo = time.time() - inicio
    print(f" Tiempo síncrono: {tiempo:.2f} segundos\n")


# 1B. Versión Asíncrona con Semáforo (Rápida - Concurrente)
async def descargar_url(client, url, semaforo):
    # El semáforo limita cuántas tareas entran aquí al mismo tiempo
    async with semaforo:
        await client.get(url)


async def fetch_asincrono():
    print("Iniciando descargas ASÍNCRONAS (todas a la vez)...")
    inicio = time.time()

    # Semáforo de 3: Máximo 3 descargas simultáneas para no saturar la red
    semaforo = asyncio.Semaphore(3)

    async with httpx.AsyncClient() as client:
        # Creamos la lista de tareas en el Event Loop
        tareas = [descargar_url(client, url, semaforo) for url in URLS]
        # asyncio.gather ejecuta todas las tareas concurrentemente
        await asyncio.gather(*tareas)

    tiempo = time.time() - inicio
    print(f" Tiempo asíncrono: {tiempo:.2f} segundos\n")


# =====================================================================
# PARTE 2: CPU BOUND (Operaciones Matemáticas Pesadas)
# =====================================================================
NUMEROS = [20_000_000, 20_000_000, 20_000_000, 20_000_000]


def calculo_pesado(n):
    """Suma raíces cuadradas. Esto quema CPU al 100%."""
    return sum(math.sqrt(i) for i in range(n))


# 2A. Versión Síncrona de CPU (Afectada por el GIL)
def cpu_sincrono():
    print("Iniciando cálculos pesados SÍNCRONOS (un núcleo de CPU)...")
    inicio = time.time()
    resultados = [calculo_pesado(n) for n in NUMEROS]
    tiempo = time.time() - inicio
    print(f" Tiempo CPU Síncrono: {tiempo:.2f} segundos\n")


# 2B. Versión Multiprocessing (Esquivando el GIL usando múltiples núcleos)
def cpu_multiproceso():
    print("Iniciando cálculos pesados MULTIPROCESO (todos los núcleos)...")
    inicio = time.time()

    # Crea un "Pool" (grupo) de procesos. Cada proceso es un Python independiente
    with ProcessPoolExecutor() as executor:
        # .map() reparte el trabajo (NUMEROS) entre todos los núcleos disponibles
        resultados = list(executor.map(calculo_pesado, NUMEROS))

    tiempo = time.time() - inicio
    print(f" Tiempo CPU Multiproceso: {tiempo:.2f} segundos\n")


# =====================================================================
# EJECUCIÓN PRINCIPAL Y MEDICIÓN
# =====================================================================
if __name__ == "__main__":
    print("========== COMPARATIVA I/O BOUND (RED) ==========")
    # Síncrono normal
    fetch_sincrono()
    # Asíncrono (Event Loop)
    asyncio.run(fetch_asincrono())

    print("========== COMPARATIVA CPU BOUND (MATEMÁTICAS) ==========")
    # Síncrono normal
    cpu_sincrono()
    # Multiprocesamiento
    cpu_multiproceso()
