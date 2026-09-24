import httpx
import typer
from pydantic_settings import BaseSettings, SettingsConfigDict


# =====================================================================
# 1. CONFIGURACIÓN POR VARIABLES DE ENTORNO (Pydantic Settings)
# =====================================================================
class Config(BaseSettings):
    """
    Lee las variables de entorno.
    Si no existen, usa los valores por defecto (localhost:8000).
    """

    api_url: str = "http://127.0.0.1:8000/api/v1/orders"
    api_token: str = "token_de_prueba"

    # Esto permite leer un archivo .env si existe en el sistema
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


config = Config()

# =====================================================================
# 2. INICIALIZAR LA APLICACIÓN TYPER (El Motor CLI)
# =====================================================================
# Typer usa type-hints para generar automáticamente la ayuda y los comandos
app = typer.Typer(help="Herramienta CLI para gestionar Órdenes de la API.")

# =====================================================================
# 3. LOS COMANDOS (Scripts de Mantenimiento / Automatización)
# =====================================================================


@app.command()
def listar():
    """Obtiene y lista todas las órdenes desde la API."""
    typer.echo(f" Consultando API en: {config.api_url} ...")

    headers = {"Authorization": f"Bearer {config.api_token}"}

    try:
        # Hacemos la llamada real a la API (Simulada si la API no está encendida)
        with httpx.Client() as client:
            response = client.get(config.api_url, headers=headers)
            response.raise_for_status()  # Lanza error si no es 200 OK

            ordenes = response.json()
            if not ordenes:
                typer.echo(" No hay órdenes registradas actualmente.")
                return

            typer.secho("\n--- LISTA DE ÓRDENES ---", fg=typer.colors.CYAN, bold=True)
            for orden in ordenes:
                typer.echo(
                    f"📦 ID: {orden.get('id')} | Producto: {orden.get('producto')} | Cantidad: {orden.get('cantidad')}"
                )

    except httpx.ConnectError:
        typer.secho(
            " ERROR: No se pudo conectar a la API. ¿Está el servidor encendido?",
            fg=typer.colors.RED,
        )
    except httpx.HTTPStatusError as e:
        typer.secho(f" ERROR de la API: {e.response.status_code}", fg=typer.colors.RED)


@app.command()
def crear(
    producto: str = typer.Argument(..., help="Nombre del producto a comprar"),
    cantidad: int = typer.Option(1, "--cantidad", "-c", help="Cantidad de items"),
    precio: float = typer.Option(0.0, "--precio", "-p", help="Precio unitario"),
):
    """Crea una nueva orden enviando los datos a la API."""
    if cantidad <= 0:
        typer.secho(" La cantidad debe ser mayor a 0", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    payload = {"producto": producto, "cantidad": cantidad, "precio": precio}
    headers = {"Authorization": f"Bearer {config.api_token}"}

    try:
        with httpx.Client() as client:
            response = client.post(config.api_url, json=payload, headers=headers)
            response.raise_for_status()

            data = response.json()
            typer.secho(
                f" ¡Éxito! Orden creada con ID: {data.get('id')}", fg=typer.colors.GREEN
            )

    except Exception as e:
        typer.secho(f" Falló la creación: {str(e)}", fg=typer.colors.RED)


@app.command()
def borrar(order_id: int = typer.Argument(..., help="El ID de la orden a eliminar")):
    """Elimina una orden de la base de datos (Requiere confirmación)."""

    # Prompt interactivo para confirmación de seguridad
    confirmacion = typer.confirm(
        f"⚠️ ¿Estás COMPLETAMENTE SEGURO de querer borrar la orden {order_id}?"
    )

    if not confirmacion:
        typer.echo("Operación cancelada.")
        raise typer.Abort()

    typer.secho(
        f"Simulando borrado de orden {order_id} en la API...", fg=typer.colors.YELLOW
    )
    # Aquí iría un client.delete(f"{config.api_url}/{order_id}")
    typer.secho("Orden borrada exitosamente.", fg=typer.colors.GREEN)


# =====================================================================
# EJECUCIÓN (Si se llama al script directamente)
# =====================================================================
if __name__ == "__main__":
    app()
