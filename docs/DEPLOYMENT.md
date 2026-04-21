# Deployment Guide

## Local Development

1. Copy `.env.example` to `.env` and update secrets.
2. Install backend packages:
   - `cd backend && python -m pip install -r requirements.txt`
3. Create local storage folder:
   - `mkdir storage`
4. Start backend server:
   - `cd backend && uvicorn app.main:app --reload --port 8000`
5. Install frontend packages:
   - `cd frontend && npm install`
6. Start frontend app:
   - `cd frontend && npm run dev`

## Production Notes

- Use PostgreSQL for `DATABASE_URL`.
- Use Redis for `REDIS_URL` and enable Celery workers.
- Enforce HTTPS with a managed TLS proxy or reverse proxy.
- Use S3-compatible storage for uploaded files.
- Set `ALLOWED_HOSTS` to your domain.
- Configure `SECRET_KEY` to a strong random value.

## Platform Deployment

- AWS: Use EC2 + RDS + ElastiCache + S3.
- GCP: Use Cloud Run / Compute Engine + Cloud SQL + Memorystore + Cloud Storage.
- Oracle Cloud: Use VM instances with PostgreSQL and object storage.

## Security Checklist

- Store JWT secrets in environment variables.
- Enable rate limiting and brute-force protection.
- Scan uploaded files before processing.
- Encrypt database and storage volumes at rest.
- Use HTTPS for all client/server communication.
