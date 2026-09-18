import logging
import time
from pathlib import Path

import httpx

# =====================================================================
# CONFIGURACIÓN AVANZADA DE LOGGING (Consola + Archivo .log)
# =====================================================================
CARPETA_ACTUAL = Path(__file__).parent
RUTA_LOG = CARPETA_ACTUAL / "app.log"

# Configuramos el formato estándar para los logs
formato_log = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")

# 1. Manejador para el archivo (FileHandler)
manejador_archivo = logging.FileHandler(RUTA_LOG, mode="a", encoding="utf-8")
manejador_archivo.setFormatter(formato_log)

# 2. Manejador para la consola/terminal (StreamHandler)
manejador_consola = logging.StreamHandler()
manejador_consola.setFormatter(formato_log)

# 3. Configuramos el Logger raíz
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Nivel mínimo a registrar
logger.addHandler(manejador_archivo)  # Agregamos la salida al archivo
logger.addHandler(manejador_consola)  # Agregamos la salida a la consola

CARPETA_ACTUAL = Path(__file__).parent
RUTA_DESCARGA_IMAGEN = CARPETA_ACTUAL / "imagen_descargada.jpg"
RUTA_DESCARGA_JSON = CARPETA_ACTUAL / "json_delay.json"


def descargar_archivo_streaming(
    url: str, destino: Path, max_reintentos: int = 3
) -> bool:
    """
    Descarga un archivo por streaming usando httpx, con manejo de errores,
    timeouts estrictos y reintentos automáticos (Backoff).
    """
    # 1. TIMEOUTS: Configuramos un límite estricto (5 seg para conectar, 10 seg en total)
    config_timeout = httpx.Timeout(10.0, connect=5.0)

    delay = 2  # Segundos de espera inicial en caso de error

    for intento in range(1, max_reintentos + 1):
        try:
            logger.info(f"Intento {intento}/{max_reintentos}: Conectando a {url}...")

            # 2. CLIENTE HTTPX ROBUSTO (Habilitando HTTP/2)
            with httpx.Client(timeout=config_timeout, http2=True) as client:

                # 3. STREAMING Y USO EFICIENTE DE MEMORIA
                # 'client.stream' mantiene la conexión abierta sin descargar el archivo a la RAM
                with client.stream("GET", url) as response:

                    # Verifica si el servidor mandó un error (ej. 404 No encontrado, 500 Error de servidor)
                    response.raise_for_status()

                    logger.info(
                        f"Conexión exitosa. Escribiendo en disco por streaming: {destino.name}"
                    )

                    # Guardamos a disco pedazo a pedazo
                    with open(destino, "wb") as archivo:
                        # Iteramos la descarga en bloques de 8KB (8192 bytes)
                        for chunk in response.iter_bytes(chunk_size=8192):
                            archivo.write(chunk)

            logger.info("✅ Descarga completada exitosamente.")
            return True  # Salimos de la función con éxito

        # 4. GESTIÓN DE RESILIENCIA Y ERRORES ESPECÍFICOS
        except httpx.TimeoutException:
            logger.warning("⚠️ Timeout: El servidor tardó demasiado en responder.")
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Error HTTP del servidor: Código {e.response.status_code}")
            # Si el error es 404 (Archivo no existe), no tiene caso seguir reintentando
            if e.response.status_code == 404:
                logger.error("El archivo no existe. Cancelando operación.")
                break
        except httpx.RequestError as e:
            logger.warning(f"⚠️ Error de red o conexión caída: {e}")

        # Lógica de reintentos
        if intento < max_reintentos:
            logger.info(f"⏳ Esperando {delay} segundos antes de reintentar...")
            time.sleep(delay)
            delay *= 2  # Aumentamos la espera: 2s, luego 4s, etc.

    logger.error("❌ Se agotaron los reintentos. Falló la descarga.")
    return False


if __name__ == "__main__":
    # URL pública de prueba que devuelve una imagen real
    URL_EXITO = "https://httpbin.org/image/jpeg"

    # URL trampa: Le dice al servidor de prueba que tarde 15 segundos en responder
    URL_TIMEOUT = "https://httpbin.org/delay/15"

    print("\n--- PRUEBA 1: DESCARGA EXITOSA (STREAMING) ---")
    descargar_archivo_streaming(URL_EXITO, RUTA_DESCARGA_IMAGEN)

    print("\n--- PRUEBA 2: SIMULANDO CAÍDA DEL SERVIDOR (TIMEOUT Y REINTENTOS) ---")
    descargar_archivo_streaming(URL_TIMEOUT, RUTA_DESCARGA_JSON)
