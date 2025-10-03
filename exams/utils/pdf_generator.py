# utils/pdf_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import HexColor
from datetime import datetime, timedelta
from minio import Minio
from minio.error import S3Error
import io
import os


def generate_exam_pdf(questions: list, title: str, description: str) -> bytes:
   
    # Crear buffer en memoria
    buffer = io.BytesIO()
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Contenedor de elementos
    story = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilo personalizado para el título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Estilo para la descripción
    description_style = ParagraphStyle(
        'CustomDescription',
        parent=styles['Normal'],
        fontSize=12,
        textColor=HexColor('#7f8c8d'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    )
    
    # Estilo para las preguntas
    question_style = ParagraphStyle(
        'Question',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor('#34495e'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    # Estilo para las respuestas
    answer_style = ParagraphStyle(
        'Answer',
        parent=styles['Normal'],
        fontSize=11,
        textColor=HexColor('#2c3e50'),
        leftIndent=20,
        spaceAfter=6,
        fontName='Helvetica'
    )
    
    # Agregar título
    story.append(Paragraph(title, title_style))
    
    # Agregar descripción
    story.append(Paragraph(description, description_style))
    
    # Agregar fecha
    date_text = f"Fecha de creación: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    story.append(Paragraph(date_text, description_style))
    
    story.append(Spacer(1, 0.3 * inch))
    
    # Separador
    story.append(Paragraph("<hr/>", styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))
    
    # Agregar preguntas y respuestas
    for idx, question_data in enumerate(questions, 1):
        # Pregunta
        question_text = f"<b>{idx}.</b> {question_data.get('question', '')}"
        story.append(Paragraph(question_text, question_style))
        
        # Respuestas
        answers = question_data.get('aswers', [])  # Nota: el JSON tiene 'aswers' (typo)
        
        for answer_idx, answer in enumerate(answers, 1):
            answer_letter = chr(64 + answer_idx)  # A, B, C, D...
            answer_text = f"{answer_letter}) {answer}"
            story.append(Paragraph(answer_text, answer_style))
        
        # Espacio entre preguntas
        story.append(Spacer(1, 0.3 * inch))
    
    # Construir PDF
    doc.build(story)
    
    # Obtener el valor del buffer
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes


def save_pdf_to_file(pdf_bytes: bytes, filename: str, directory: str = "exams") -> str:

    # Crear directorio si no existe
    os.makedirs(directory, exist_ok=True)
    
    # Ruta completa
    file_path = os.path.join(directory, filename)
    
    # Guardar PDF
    with open(file_path, 'wb') as f:
        f.write(pdf_bytes)
    
    return file_path


def upload_pdf_to_minio(
    pdf_bytes: bytes,
    filename: str,
    bucket_name: str = "exams",
    endpoint: str = "localhost:9000",
    access_key: str = "minioadmin",
    secret_key: str = "minioadmin123",
    secure: bool = False
) -> dict:
   
    try:
        # Crear cliente de MinIO
        client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
        
        # Verificar si el bucket existe, si no, crearlo
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' creado exitosamente")
        
        # Convertir bytes a BytesIO para subir
        pdf_stream = io.BytesIO(pdf_bytes)
        file_size = len(pdf_bytes)
        
        # Subir el archivo
        result = client.put_object(
            bucket_name,
            filename,
            pdf_stream,
            file_size,
            content_type='application/pdf'
        )
        
        # Generar URL del archivo (válida por 7 días por defecto)
        file_url = client.presigned_get_object(bucket_name, filename, expires=timedelta(days=7))
        
        return {
            "success": True,
            "bucket": bucket_name,
            "filename": filename,
            "size": file_size,
            "etag": result.etag,
            "url": file_url,
            "message": f"Archivo subido exitosamente a MinIO"
        }
        
    except S3Error as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error al subir archivo a MinIO"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error inesperado al subir archivo"
        }