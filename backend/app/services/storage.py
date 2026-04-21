import shutil
from pathlib import Path
from fastapi import UploadFile
from ..config import UPLOADED_PATH


def save_upload(uploaded_file: UploadFile, target_dir: Path = UPLOADED_PATH) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # NAYA FIX: Agar filename None aata hai, toh default naam assign hoga
    safe_filename = uploaded_file.filename if uploaded_file.filename else "unnamed_upload.pdf"
    
    
    file_path = target_dir / safe_filename
    
    with file_path.open('wb') as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)
        
    return file_path


def resolve_report_path(filename: str) -> Path:
    from ..config import REPORTS_PATH
    REPORTS_PATH.mkdir(parents=True, exist_ok=True)
    return REPORTS_PATH / filename