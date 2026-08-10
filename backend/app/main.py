# ============================================================
# NexRay AI - Main Application Entry Point
# ============================================================

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from app.database import engine
from app.models import Base
from app.routes.xray import router as xray_router
from app.routes.symptoms import router as symptoms_router
from app.routes.reports import router as reports_router
from app.routes.auth import router as auth_router
from app.routes.refine import router as refine_router
from app.routes.combined import router as combined_router
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NexRay AI",
    description="AI-Powered Medical Assistant Platform",
    version="1.0.0"
)

# ── CORS Middleware ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",                    # Local development
        "https://nexray-ai.vercel.app",             # Vercel deployment
        "https://*.vercel.app",                     # Any Vercel preview URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global Error Handler ──
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "An unexpected error occurred",
            "detail": str(exc),
            "path": str(request.url)
        }
    )

# ── Register All Routers ──
app.include_router(xray_router)
app.include_router(symptoms_router)
app.include_router(reports_router)
app.include_router(auth_router)
app.include_router(refine_router)
app.include_router(combined_router)

# ── Root Route ──
@app.get("/")
def root():
    return {
        "message": "Welcome to NexRay AI",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }

# ── Health Check Route ──
@app.api_route("/health", methods=["GET", "HEAD"])
def health_check():
    return {"status": "healthy"}