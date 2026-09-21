from typing import Any, Dict, List

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field

# 1. ROUTER: Para no tener todo en un solo archivo
router = APIRouter(prefix="/orders", tags=["Orders"])

# 2. DB TEMPORAL: Un simple diccionario en memoria
db_temporal: Dict[int, Dict[str, Any]] = {}


# 3. ESQUEMAS PYDANTIC: Validación de datos de entrada y salida
class OrderCreate(BaseModel):
    producto: str = Field(..., min_length=3)
    cantidad: int = Field(..., gt=0)
    precio: float = Field(..., gt=0.0)


class OrderResponse(OrderCreate):
    id: int


# 4. DEPENDENCIA DE AUTENTICACIÓN (JWT)
SECRET_KEY = "mi_clave_super_secreta"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")


def obtener_usuario_actual(token: str = Depends(oauth2_scheme)) -> str:
    """Verifica el JWT. Si es inválido, rechaza la petición."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub", "")
        if not username:
            raise ValueError()
        return username
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


# 5. ENDPOINTS CRUD PROTEGIDOS
@router.post("/", response_model=OrderResponse)
def crear_orden(
    orden: OrderCreate, usuario: str = Depends(obtener_usuario_actual)
) -> OrderResponse:
    nuevo_id = len(db_temporal) + 1
    nueva_orden = {"id": nuevo_id, **orden.model_dump()}
    db_temporal[nuevo_id] = nueva_orden
    return OrderResponse(**nueva_orden)


@router.get("/", response_model=List[OrderResponse])
def listar_ordenes(
    usuario: str = Depends(obtener_usuario_actual),
) -> List[OrderResponse]:
    return [OrderResponse(**orden) for orden in db_temporal.values()]
