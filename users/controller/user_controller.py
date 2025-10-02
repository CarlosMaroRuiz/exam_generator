from core.db import SQLiteDB
from core.security.generate_token import generar_token


class UserController:
    def __init__(self):
        pass

    def register_user(self, user_data):
        db = SQLiteDB()
        email = user_data.get("email")
        password = user_data.get("password")
        
        try:
            existing_user = db.fetchone(
                "SELECT * FROM usuario WHERE email = ?",
                (email,)
            )
            
            if existing_user:
                return {"error": "User already exists"}
            
       
            db.execute(
                "INSERT INTO usuario (email, password) VALUES (?, ?)",
                (email, password)
            )
            
            print("User registered successfully")
            return {"message": "User registered successfully"}
            
        except Exception as e:
            return {"error": str(e)}

    def login_user(self, credentials):
        db = SQLiteDB()
        email = credentials.get("email")
        password = credentials.get("password")
        
        try:
            user = db.fetchone(
                "SELECT * FROM usuario WHERE email = ? AND password = ?",
                (email, password)
            )
            
            if user:
                token = generar_token(user[0])

                return {
                    "message": "User logged in successfully",
                    "token": token
                }
            else:
                return {"error": "Invalid credentials"}
                
        except Exception as e:
            return {"error": str(e)}