from core.db import SQLiteDB
from agent import execute_agent
from ..utils import generate_exam_pdf, upload_pdf_to_minio, delete_pdf_from_minio
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()


class ExamController:
    def __init__(self):
        self.minio_config = {
            "endpoint": os.getenv("MINIO_ENDPOINT"),
            "access_key": os.getenv("MINIO_ACCESS_KEY"),
            "secret_key": os.getenv("MINIO_SECRET_KEY"),
            "secure": os.getenv("MINIO_SECURE") == "True",
            "bucket_name": os.getenv("MINIO_BUCKET")
        }

    async def create_exam(self, exam_data: dict, user_id: int):
        db = SQLiteDB()
        title = exam_data.get("title")
        description = exam_data.get("description")
        
        if not title:
            return {"error": "Title is required"}

        try:
            exist_file = db.fetchone(
                "SELECT * FROM examen WHERE titulo = ? AND id_usuario = ?",
                (title, user_id)
            )
            if exist_file:
                return {"msg": "Examen con ese título ya existe"}
            
            result = await execute_agent(description)
            
            # Convertir objetos Question a diccionarios
            questions_list = [
                {
                    'question': q.question,
                    'aswers': q.aswers,
                    'correct_answer': q.correct_answer
                }
                for q in result
            ]
            
            # Generar PDF
            pdf_bytes = generate_exam_pdf(questions_list, title, description)
            
            # Nombre del archivo
            pdf_filename = f"exam_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # Subir a MinIO
            minio_result = upload_pdf_to_minio(
                pdf_bytes=pdf_bytes,
                filename=pdf_filename,
                bucket_name=self.minio_config["bucket_name"],
                endpoint=self.minio_config["endpoint"],
                access_key=self.minio_config["access_key"],
                secret_key=self.minio_config["secret_key"],
                secure=self.minio_config["secure"]
            )
            
            if not minio_result.get("success"):
                return {
                    "error": minio_result.get("error"),
                    "message": "Error al subir PDF a MinIO"
                }
            
            db.execute(
                "INSERT INTO examen (titulo, id_usuario, url_bucket) VALUES (?, ?, ?)",
                (title, user_id, minio_result["url"])
            )
            
            return {
                "msg": "Exam created successfully",
                "exam": {
                    "title": title,
                    "description": "Examen sobre Widgets de Flutter",
                    "result": questions_list,
                    "pdf_url": minio_result["url"],
                    "pdf_filename": pdf_filename,
                }
            }

        except Exception as e:
            return {"error": str(e)}
        
    async def get_exams_by_user(self, user_id: int):
        db = SQLiteDB()
        try:
            exams = db.fetchall(
                "SELECT * FROM examen WHERE id_usuario = ?",
                (user_id,)
            )
            exam_list = [
                {
                    "id": exam[0],
                    "title": exam[3],
                    "url_bucket": exam[1]
                }
                for exam in exams
            ]
            return exam_list
        except Exception as e:
            return {"error": str(e)}
        
    async def delete_exam_user(self, user_id: int, exam_id: int):
        db = SQLiteDB()
        try:
            # Buscar examen en BD
            exam = db.fetchone(
                "SELECT id, url_bucket FROM examen WHERE id = ? AND id_usuario = ?",
                (exam_id, user_id)
            )

            if not exam:
                return {"error": "Exam not found or not owned by user"}

            exam_id, url_bucket = exam

            # Extraer nombre del archivo desde la URL (antes del '?')
            filename = url_bucket.split("/")[-1].split("?")[0]

            delete_result = delete_pdf_from_minio(
                filename=filename,
                bucket_name=self.minio_config["bucket_name"],
                endpoint=self.minio_config["endpoint"],
                access_key=self.minio_config["access_key"],
                secret_key=self.minio_config["secret_key"],
                secure=self.minio_config["secure"]
            )

            if not delete_result["success"]:
                return {"error": f"No se pudo eliminar de MinIO: {delete_result['error']}"}

            
            db.execute("DELETE FROM examen WHERE id = ? AND id_usuario = ?", (exam_id, user_id))

            return {"msg": "Exam eliminado correctamente"}

        except Exception as e:
            return {"error": str(e)}