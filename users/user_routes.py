from fastapi import APIRouter,HTTPException
from .controller import UserController
from .schemas import UserRegister,UserLogin

controller = UserController()

user_routes = APIRouter(
    prefix='/auth'
)

@user_routes.post('/register')
def register_user(user_data: UserRegister):

    result = controller.register_user(user_data.dict())
    # Maneja los errores
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@user_routes.post('/login')
def login_user(credentials: UserLogin):
    result = controller.login_user(credentials.dict())
    
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    
    return result