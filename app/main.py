"""
AcadGuard - Academic Project Management & Plagiarism Detection System
Main FastAPI Application Entrypoint.
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from app.core.config import settings
from app.database import engine, Base
from app.seed import seed_data
from app.routers import (
    auth_router,
    users_router,
    projects_router,
    submissions_router,
    plagiarism_router,
    supervision_router,
    dashboard_router,
    notifications_router,
    admin_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context for initialization and cleanup."""
    # Initialize DB tables and seed data
    Base.metadata.create_all(bind=engine)
    seed_data()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A centralized academic project management system with automated plagiarism detection, supervisor review workflows, and institutional integrity reporting.",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global API Router Prefix
api_prefix = settings.API_V1_STR
app.include_router(auth_router, prefix=api_prefix)
app.include_router(users_router, prefix=api_prefix)
app.include_router(projects_router, prefix=api_prefix)
app.include_router(submissions_router, prefix=api_prefix)
app.include_router(plagiarism_router, prefix=api_prefix)
app.include_router(supervision_router, prefix=api_prefix)
app.include_router(dashboard_router, prefix=api_prefix)
app.include_router(notifications_router, prefix=api_prefix)
app.include_router(admin_router, prefix=api_prefix)

# Mount frontend static files directory
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
os.makedirs(frontend_path, exist_ok=True)
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/health")
def health_check():
    """System health check endpoint."""
    return {"status": "healthy", "service": "AcadGuard Backend", "version": settings.VERSION}

# Direct HTML page routes
@app.get("/")
async def serve_index():
    index_file = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse({"message": "AcadGuard API is online. Frontend assets loading..."})

@app.get("/login")
async def serve_login():
    login_file = os.path.join(frontend_path, "login.html")
    if os.path.exists(login_file):
        return FileResponse(login_file)
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/register")
async def serve_register():
    reg_file = os.path.join(frontend_path, "register.html")
    if os.path.exists(reg_file):
        return FileResponse(reg_file)
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/app")
async def serve_app():
    app_file = os.path.join(frontend_path, "app.html")
    if os.path.exists(app_file):
        return FileResponse(app_file)
    return FileResponse(os.path.join(frontend_path, "index.html"))

# Catch-all client-side route fallback for student, supervisor, and admin paths
@app.get("/{full_path:path}")
async def client_fallback(full_path: str):
    # Check if a static file was requested directly
    possible_file = os.path.join(frontend_path, full_path)
    if os.path.isfile(possible_file):
        return FileResponse(possible_file)
    
    # SPA routes: student/*, supervisor/*, admin/*, reports/*
    if full_path.startswith(("student", "supervisor", "admin", "reports")):
        app_file = os.path.join(frontend_path, "app.html")
        if os.path.exists(app_file):
            return FileResponse(app_file)

    index_file = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse({"status": "AcadGuard system running"})
