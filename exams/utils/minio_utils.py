from minio import Minio

def delete_pdf_from_minio(filename: str, bucket_name: str, endpoint: str, access_key: str, secret_key: str, secure: bool = False):
    try:
        client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )

        client.remove_object(bucket_name, filename)
        return {"success": True, "msg": f"{filename} eliminado correctamente del bucket {bucket_name}"}

    except Exception as e:
        return {"success": False, "error": str(e)}
