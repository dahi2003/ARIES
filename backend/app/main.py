from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware import Middleware
from fastapi.staticfiles import StaticFiles

from .config import ALLOWED_HOSTS, FORCE_HTTPS, REPORTS_PATH
from .database import engine
from .models import Base
from .routers import auth, users, uploads, evaluations, results

Base.metadata.create_all(bind=engine)

middleware = [
    Middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS),
]

app = FastAPI(
    title='Smart Exam Copy Evaluation System',
    description='Backend API for upload, OCR, grading, and reporting.',
    version='1.0.0',
    middleware=middleware,
)

if FORCE_HTTPS:
    from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
    app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Mount static files for reports
app.mount("/api/reports", StaticFiles(directory=str(REPORTS_PATH)), name="reports")

app.include_router(auth)
app.include_router(users)
app.include_router(uploads)
app.include_router(evaluations)
app.include_router(results)

@app.middleware('http')
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'same-origin'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

@app.get('/')
def health_check():
    return {'status': 'ok', 'message': 'Smart Exam Copy Evaluation System backend is running.'}
