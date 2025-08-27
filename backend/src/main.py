"""FastAPI main application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from src.api.routers import router
from src.database.models import mongodb
from src.core.config import PROJECT_NAME, PROJECT_DESCRIPTION, PROJECT_VERSION

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting Contract Intelligence Parser API")
    try:
        result = mongodb.connect()
        if result is not None:
            logger.info("Connected to MongoDB successfully")
        else:
            logger.warning("Starting without MongoDB - upload features will be limited")
    except Exception as e:
        logger.warning(f"MongoDB connection failed: {e} - continuing without MongoDB")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Contract Intelligence Parser API")
    mongodb.disconnect()


# Create FastAPI application
app = FastAPI(
    title=PROJECT_NAME,
    description=PROJECT_DESCRIPTION,
    version=PROJECT_VERSION,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router)


@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "Contract Intelligence Parser API",
        "version": PROJECT_VERSION,
        "docs": "/docs",
        "health": "/api/v1/health"
    }


@app.get("/favicon.ico")
def favicon():
    """Favicon endpoint"""
    return {"message": "No favicon"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
