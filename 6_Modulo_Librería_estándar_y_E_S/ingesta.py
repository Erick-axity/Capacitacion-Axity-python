import csv
import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from zoneinfo import ZoneInfo

# =====================================================================
# 1. LOGGING ESTRUCTURADO: Reemplazando a "print()"
# =====================================================================
# Configuramos el logger para que muestre: Fecha/Hora - Nivel - Mensaje
logging.basicConfig(
    level=logging.DEBUG,  # Captura desde nivel DEBUG hacia arriba (INFO, WARNING, ERROR)
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# =====================================================================
# 2. PATHLIB Y MANEJO DE RUTAS SEGURO
# =====================================================================
# Definimos las rutas usando objetos Path (orientado a objetos, seguro)
CARPETA_ACTUAL = Path(__file__).parent
RUTA_CSV = CARPETA_ACTUAL / "ventas.csv"
RUTA_JSON = CARPETA_ACTUAL / "metricas_salida.json"


def procesar_datos() -> None:
    # Verificación segura de archivos con Pathlib
    if not RUTA_CSV.exists():
        logger.error(f"El archivo {RUTA_CSV.name} no existe. Abortando.")
        return

    logger.info("Iniciando la ingesta de datos del archivo CSV...")

    ventas_validas: List[Dict[str, Any]] = []
    total_ingresos = 0.0

    # =====================================================================
    # 3. CSV: INGESTA Y PARSEO
    # =====================================================================
    with open(RUTA_CSV, mode="r", encoding="utf-8") as archivo_csv:
        # DictReader lee la primera fila como llaves del diccionario
        lector = csv.DictReader(archivo_csv)

        for fila in lector:
            producto = fila.get("producto", "Desconocido")
            try:
                # Si falta la cantidad, esto fallará y lanzará ValueError
                cantidad = int(fila["cantidad"])
                precio = float(fila["precio"])

                subtotal = cantidad * precio
                total_ingresos += subtotal

                ventas_validas.append(
                    {"producto": producto, "cantidad": cantidad, "subtotal": subtotal}
                )
                logger.debug(f"Fila procesada correctamente: {producto}")

            except ValueError:
                # Uso del nivel WARNING para datos faltantes o corruptos
                logger.warning(
                    f"Dato corrupto o faltante en producto '{producto}'. Fila ignorada."
                )

    # =====================================================================
    # 4. DATETIME Y ZONAS HORARIAS
    # =====================================================================
    # Registramos el momento exacto usando la zona horaria de México (ejemplo)
    zona_mexico = ZoneInfo("America/Mexico_City")
    marca_tiempo = datetime.now(zona_mexico).isoformat()

    # Métrica final
    metricas = {
        "generado_en": marca_tiempo,
        "registros_exitosos": len(ventas_validas),
        "total_ingresos_usd": total_ingresos,
        "detalle": ventas_validas,
    }

    # =====================================================================
    # 5. JSON: SERIALIZACIÓN Y EXPORTACIÓN
    # =====================================================================
    logger.info("Calculadas las métricas. Exportando a JSON...")
    with open(RUTA_JSON, mode="w", encoding="utf-8") as archivo_json:
        # dump() serializa el diccionario y lo guarda en el archivo con sangría de 4 espacios
        json.dump(metricas, archivo_json, indent=4)

    logger.info(f"Exportación exitosa. Archivo creado en: {RUTA_JSON.name}")

    # =====================================================================
    # 6. SUBPROCESS Y AUTOMATIZACIÓN
    # =====================================================================
    logger.info("Ejecutando automatización de sistema con subprocess (Git status)...")
    try:
        # subprocess.run ejecuta comandos del sistema operativo real
        resultado = subprocess.run(
            ["git", "status", "-s"], capture_output=True, text=True
        )
        logger.info(f"Estado de archivos en Git:\n{resultado.stdout.strip()}")
    except Exception as e:
        logger.error(f"Falló la ejecución del comando de sistema: {e}")


if __name__ == "__main__":
    procesar_datos()
