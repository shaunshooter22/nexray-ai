# ============================================================
# NexRay AI - Main Application Entry Point
# This is the starting point of the entire backend.
# FastAPI is initialized here and all settings are applied.
# ============================================================

from fastapi import FastAPI, Request  # FastAPI tools
from fastapi.middleware.cors import CORSMiddleware  # CORS middleware
from fastapi.responses import JSONResponse  # For returning JSON error responses
from dotenv import load_dotenv  # For reading the .env file
from app.database import engine  # Database engine
from app.models import Base  # Database models
from app.routes.xray import router as xray_router  # X-ray routes
from app.routes.symptoms import router as symptoms_router  # Symptom routes
from app.routes.reports import router as reports_router  # Report routes
from app.routes.auth import router as auth_router  # Import the auth routes
from app.routes.refine import router as refine_router  # Import the refine routes
from app.routes.combined import router as combined_router  # Import the combined route
import logging  # For logging errors


# Set up logging so errors are printed clearly in the terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load all environment variables from .env file
load_dotenv()

# Create all database tables if they dont exist
Base.metadata.create_all(bind=engine)

# Create the FastAPI app
app = FastAPI(
    title="NexRay AI",
    description="AI-Powered Medical Assistant Platform",
    version="1.0.0"
)

# ── CORS Middleware ──
# Allows the React frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global Error Handler ──
# Catches any unhandled errors and returns a clean JSON response
# instead of crashing with a 500 Internal Server Error
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the error to the terminal so we can debug it
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
app.include_router(xray_router)       # X-ray analysis routes
app.include_router(symptoms_router)   # Symptom checker routes
app.include_router(reports_router)    # Report generation routes
app.include_router(auth_router)  # Register the auth routes
app.include_router(refine_router)  # Register the refine routes
app.include_router(combined_router)  # Register the combined route

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
@app.get("/health")
def health_check():
    return {"status": "healthy"}