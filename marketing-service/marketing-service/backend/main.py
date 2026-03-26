from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router

app = FastAPI(
    title="Marketing Service API",
    description="A scalable marketing campaign management API built with Python FastAPI, containerized with Docker, deployed via GitHub Actions on AWS EKS with Kubernetes.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "service": "Marketing Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
