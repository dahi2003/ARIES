import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '..' / '.env')

SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-secret')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '60'))
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR.parent / "backend.db"}')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
STORAGE_PATH = Path(os.getenv('STORAGE_PATH', BASE_DIR.parent / 'storage'))
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
FORCE_HTTPS = os.getenv('FORCE_HTTPS', 'false').lower() in {'1', 'true', 'yes'}

STORAGE_PATH.mkdir(parents=True, exist_ok=True)
REPORTS_PATH = STORAGE_PATH / 'reports'
REPORTS_PATH.mkdir(parents=True, exist_ok=True)
UPLOADED_PATH = STORAGE_PATH / 'uploads'
UPLOADED_PATH.mkdir(parents=True, exist_ok=True)
