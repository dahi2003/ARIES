# Smart Exam Copy Evaluation System

A production-ready web platform built with FastAPI backend and React frontend for professors to upload answer keys, student answer sheets, and automatically evaluate exam copies using OCR and NLP-powered grading.

## Structure

- `backend/`: FastAPI REST API, authentication, evaluation pipeline, PDF report generation
- `frontend/`: React + Vite UI for professors and students
- `docs/`: architecture, deployment, database schema, and security guidance

## Local run

1. Install backend dependencies:
   - `cd backend && python -m pip install -r requirements.txt`
2. Start backend:
   - `cd backend && uvicorn app.main:app --reload --port 8000`
3. Install frontend dependencies:
   - `cd frontend && npm install`
4. Start frontend:
   - `cd frontend && npm run dev`

## Notes

- The system uses JWT authentication and role-based authorization.
- File uploads are validated and stored locally in `storage/`.
- OCR extraction supports PDFs and images; OpenAI NLP scoring is optional via `OPENAI_API_KEY`.
- The app uses background evaluation jobs and is designed for easy scaling with Redis/Celery in production.
