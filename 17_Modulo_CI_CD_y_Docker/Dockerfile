# STAGE 1: BUILDER
FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=2.0.0

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app

# 1. Ya NO copiamos el poetry.lock, solo el TOML
COPY pyproject.toml ./

# 2. Usamos el flag oficial que dice "no uses archivos lock, haz la instalación fresca"
RUN poetry config virtualenvs.create false \
    && poetry install --no-root

# STAGE 2: PRODUCTION
FROM python:3.12-slim AS production

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY modulo_ci_cd_y_docker /app/modulo_ci_cd_y_docker

RUN useradd -m myuser

USER myuser

EXPOSE 8000

CMD ["uvicorn", "modulo_ci_cd_y_docker.main:app", "--host", "0.0.0.0", "--port", "8000"]