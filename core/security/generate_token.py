from core.config import config
from typing import Dict
from jose import jwt
def generar_token(user_id: int) -> str:
    payload: Dict = {"sub": str(user_id)}
    return  jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM)