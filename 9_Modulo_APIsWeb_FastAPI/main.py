import time

import jwt
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

# Importamos nuestro router separado
from rutas_orders import SECRET_KEY
from rutas_orders import router as orders_router

app = FastAPI(title="API Automatización", version="1.0")

# 1. MIDDLEWARES Y CORS
# Permite que frontends en otros dominios consuman esta API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom Middleware: Mide cuánto tarda cada petición
@app.middleware("http")
async def medir_tiempo_respuesta(request: Request, call_next):
    inicio = time.time()
    response = await call_next(request)
    tiempo_total = time.time() - inicio
    response.headers["X-Process-Time"] = str(tiempo_total)
    return response


# 2. ENDPOINT DE LOGIN JWT BÁSICO
@app.post("/api/v1/login")
def login_jwt(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    # Simulación de validación de base de datos
    if form_data.username == "admin" and form_data.password == "123":
        # Generamos el Token
        token = jwt.encode({"sub": form_data.username}, SECRET_KEY, algorithm="HS256")
        return {"access_token": token, "token_type": "bearer"}

    raise HTTPException(status_code=400, detail="Credenciales incorrectas")


# 3. CONECTAMOS LA ESTRUCTURA DEL PROYECTO
app.include_router(orders_router, prefix="/api/v1")
