# Architecture Overview

## System Layers

- **Frontend**: React + Vite single-page application providing Professor and Student dashboards.
- **Backend**: FastAPI REST API handling authentication, uploads, evaluation pipeline, PDF report generation, and results retrieval.
- **Persistence**:
  - PostgreSQL-compatible relational DB for users, subjects, answer keys, student copies, and evaluations.
  - Redis for caching and queue orchestration.
  - Local storage / S3-compatible storage for uploaded documents and generated reports.

## Core Components

1. **Auth Service**: JWT-based authentication with RBAC for `superadmin`, `professor`, and `student`.
2. **Upload Service**: Handles secure file uploads, content validation, and storage.
3. **OCR Service**: Extracts text from PDF/image submissions using Tesseract and PDF conversion.
4. **Grading Engine**: Evaluates answers with exact matching, semantic similarity, and weighted scoring.
5. **Reporting**: Generates result PDFs and feedback for each student.
6. **Dashboard**: Professor sees upload progress, evaluation status, and analytics; students see marks and feedback.

## Data Flow

1. Professor logs in and uploads an answer key and a batch of student copies.
2. Backend stores files, validates format, and extracts text if possible.
3. An evaluation task is queued or run in background.
4. Grading engine compares answers against the key and assigns marks.
5. Results are stored, report PDFs are generated, and dashboards update in real time.

## Scalability Notes

- API is asynchronous and designed for horizontal scaling behind a load balancer.
- File storage can migrate to S3-compatible object storage.
- Redis-backed task queue can be enabled for distributed evaluation workloads.
- Database connection pooling and caching support high concurrency.
