FROM python:3.12-slim

# 1. ACTUALIZACIÓN DE SEGURIDAD DEL SISTEMA OPERATIVO
# Evita que el contenedor traiga vulnerabilidades de Linux de fábrica
RUN apt-get update && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. CREACIÓN DE USUARIO SIN PRIVILEGIOS (Non-Root)
# Un hacker que entre aquí no podrá instalar virus ni borrar el sistema
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# 3. CAMBIAR PROPIETARIO DE LOS ARCHIVOS
# Copiamos el código, pero le decimos a Docker que el dueño es 'appuser'
COPY --chown=appuser:appgroup seguridad.py .
COPY --chown=appuser:appgroup .env .

# 4. INSTALACIÓN DE LIBRERÍAS DE FORMA SEGURA
RUN pip install --no-cache-dir pydantic-settings

# 5. RETIRAR PERMISOS DE ROOT AL CONTENEDOR
USER appuser

# 6. RESTRICCIÓN DE PUERTOS
EXPOSE 8080

CMD ["python", "seguridad.py"]