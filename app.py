from core.db import crear_base_de_datos
from fastapi import FastAPI
from users import user_routes
from exams import exam_routes

# Crear la base de datos al iniciar la aplicación
crear_base_de_datos()
app = FastAPI()

# empezamos incluir las rutas de la aplicacion
app.include_router(user_routes)
app.include_router(exam_routes)
