from core.db import crear_base_de_datos
from fastapi import FastAPI
from users import user_routes
from exams import exam_routes


crear_base_de_datos()
app = FastAPI()


app.include_router(user_routes)
app.include_router(exam_routes)
