from fastapi import Depends, APIRouter
from .controller import ExamController
from .schemas import TestCreate
from core.security import validar_token_dependency  

controller = ExamController()

exam_routes = APIRouter(
    prefix='/exam'
)

@exam_routes.post("/create")
async def create_exam(
    exam_data: TestCreate,
    payload: dict = Depends(validar_token_dependency)
):

    user_id = payload.get("sub")
    result = await controller.create_exam(exam_data.dict(), user_id)
    return result


@exam_routes.get("/list")
async def list_pdfs(
    payload: dict = Depends(validar_token_dependency)
):
    user_id = payload.get("sub")
    result = await controller.get_exams_by_user(user_id)

    return result


@exam_routes.delete("/delete/{exam_id}")
async def delete_exam(
    exam_id: int,
    payload: dict = Depends(validar_token_dependency)
):
    user_id = payload.get("sub")
    result = await controller.delete_exam_user(user_id, exam_id)
    return result
