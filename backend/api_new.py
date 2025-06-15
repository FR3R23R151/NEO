"""
NEO Backend API

Main FastAPI application with authentication, database, and isolator integration.
Replaces Supabase-based architecture with local services.
"""

import logging
import asyncio
import sys
import time
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from services.database import db_service
from services.auth import auth_service
from services.storage import storage_service
from api.auth import router as auth_router
from api.isolator import router as isolator_router
from utils.config import config
from utils.logger import logger

# Import existing modules (updated to work with new architecture)
from agentpress.thread_manager import ThreadManager
from agent import api as agent_api
from sandbox import api as sandbox_api
from services import billing as billing_api
from flags import api as feature_flags_api
from services import transcription as transcription_api
from services.mcp_custom import discover_custom_tools
from services import email_api

load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Initialize managers
instance_id = "single"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info(f"Starting NEO Backend API with instance ID: {instance_id}")
    
    try:
        # Initialize services
        await db_service.initialize()
        await storage_service.initialize()
        
        # Initialize existing modules with new database service
        agent_api.initialize(db_service, instance_id)
        sandbox_api.initialize(db_service, instance_id)
        billing_api.initialize(db_service)
        feature_flags_api.initialize(db_service)
        transcription_api.initialize(db_service)
        email_api.initialize(db_service)
        
        # Discover custom tools
        await discover_custom_tools()
        
        logger.info("NEO Backend API started successfully")
        yield
        
    except Exception as e:
        logger.error(f"Failed to start NEO Backend API: {e}")
        raise
    finally:
        # Cleanup
        await db_service.close()
        logger.info("NEO Backend API shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="NEO Backend API",
    description="Backend API for NEO - Open Source Generalist AI Agent",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for production
if config.ENV_MODE.value == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure appropriately for production
    )

# Include routers
app.include_router(auth_router)
app.include_router(isolator_router)

# Include existing API routers (these will need to be updated)
app.include_router(agent_api.router, prefix="/agent")
app.include_router(sandbox_api.router, prefix="/sandbox")
app.include_router(billing_api.router, prefix="/billing")
app.include_router(feature_flags_api.router, prefix="/flags")
app.include_router(transcription_api.router, prefix="/transcription")
app.include_router(email_api.router, prefix="/email")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "NEO Backend API",
        "version": "2.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check database connection
        await db_service.execute_query("SELECT 1", fetch="val")
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": "healthy",
                "storage": "healthy",
                "isolator": "healthy"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log all requests."""
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} in {process_time:.4f}s")
    
    return response

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api_new:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )