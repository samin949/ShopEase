import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///shopease.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:8000').split(',')
    CORS_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]
