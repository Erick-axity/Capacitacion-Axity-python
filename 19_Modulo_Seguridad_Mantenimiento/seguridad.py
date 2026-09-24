from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


# =====================================================================
# GESTIÓN DE SECRETOS ESTRICTA
# =====================================================================
class ConfiguracionSegura(BaseSettings):
    """
    Usa 'SecretStr' en lugar de 'str'.
    Esto evita que la contraseña se filtre accidentalmente en logs o errores.
    """

    db_password: SecretStr
    api_key: SecretStr

    # Lee las credenciales desde el archivo .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Instanciamos la configuración
config = ConfiguracionSegura()

if __name__ == "__main__":
    print("--- PRUEBA DE FILTRADO DE LOGS ---")

    # Intento de un Junior de imprimir la configuración (Accidente común)
    print(f"Log accidental (La contraseña está a salvo): {config.db_password}")

    # Uso correcto por un Senior (Desencriptando solo en el instante necesario)
    conexion_db = f"mysql://admin:{config.db_password.get_secret_value()}@localhost/db"
    print("Conexión a DB generada en memoria de forma segura.")
