from dotenv import load_dotenv
import os
load_dotenv()
class Config:
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")

config = Config()