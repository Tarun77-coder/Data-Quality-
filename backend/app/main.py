from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import FRONTEND_URL
from app.routers import checks, results, upload

app = FastAPI(
    title="Data Quality Auditor API",
    version="1.0.0",
    description="Upload datasets, run data-quality checks, and export issue reports.",
)

allowed_origins = ["*"] if FRONTEND_URL == "*" else [FRONTEND_URL]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(checks.router, prefix="/checks", tags=["checks"])
app.include_router(results.router, prefix="/results", tags=["results"])


@app.get("/")
def root():
    return {"name": "Data Quality Auditor API", "status": "ok"}


@app.get("/health")
def health():
    return {"status": "ok"}
