# 🤖 ARIES: Automated Response Intelligence Evaluation System

A production-ready, Full-Stack AI platform designed for universities and professors to automate the evaluation of handwritten student exam copies. Built with a decoupled architecture using FastAPI, React, and Google's Gemini Vision AI.

## 🚀 Key Features
* **AI-Powered Grading:** Uses Gemini 2.5 Flash for high-accuracy OCR and contextual NLP evaluation of handwritten answers against official answer keys.
* **Role-Based Access:** Secure dashboards for both Professors (Upload & Evaluate) and Students (View Results).
* **Automated Processing:** Background task execution for converting PDFs to images and processing large batches of exam sheets.
* **Modern Stack:** Fast REST APIs with Python/FastAPI, responsive UI with React + Vite, and robust cloud data management.

## 📂 Project Structure
* `backend/`: FastAPI REST API, JWT authentication, Gemini AI evaluation pipeline, and PDF processing logic.
* `frontend/`: React + Vite SPA (Single Page Application) for the user interface.
* `docs/`: System architecture, deployment guides, and database schema diagrams.

## 🛠️ Local Development Setup

### 1. Backend (FastAPI + AI Engine)
```bash
cd backend
# Create a .env file and add your GEMINI_API_KEY and DATABASE_URL
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
