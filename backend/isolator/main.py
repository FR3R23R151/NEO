"""
NEO Isolator Service

A secure container isolation service for executing agent code safely.
Replaces Daytona with a custom Docker-based solution.
"""

import os
import asyncio
import logging
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from isolator import NEOIsolator
from models import (
    CreateContainerRequest,
    ContainerResponse,
    ExecuteCommandRequest,
    ExecuteCommandResponse,
    FileOperationRequest,
    FileOperationResponse
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="NEO Isolator Service",
    description="Secure container isolation service for NEO agents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize isolator
isolator = NEOIsolator()

@app.on_event("startup")
async def startup_event():
    """Initialize the isolator service."""
    logger.info("Starting NEO Isolator Service...")
    await isolator.initialize()
    logger.info("NEO Isolator Service started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down NEO Isolator Service...")
    await isolator.cleanup()
    logger.info("NEO Isolator Service shut down")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "neo-isolator"}

@app.post("/containers", response_model=ContainerResponse)
async def create_container(request: CreateContainerRequest):
    """Create a new isolated container."""
    try:
        container_id = await isolator.create_container(
            image=request.image,
            workspace_id=request.workspace_id,
            environment=request.environment,
            memory_limit=request.memory_limit,
            cpu_limit=request.cpu_limit,
            timeout=request.timeout
        )
        return ContainerResponse(
            container_id=container_id,
            status="created",
            workspace_id=request.workspace_id
        )
    except Exception as e:
        logger.error(f"Failed to create container: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/containers/{container_id}", response_model=ContainerResponse)
async def get_container(container_id: str):
    """Get container information."""
    try:
        container_info = await isolator.get_container_info(container_id)
        return ContainerResponse(**container_info)
    except Exception as e:
        logger.error(f"Failed to get container info: {e}")
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/containers/{container_id}")
async def delete_container(container_id: str):
    """Delete a container."""
    try:
        await isolator.delete_container(container_id)
        return {"status": "deleted", "container_id": container_id}
    except Exception as e:
        logger.error(f"Failed to delete container: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/containers/{container_id}/execute", response_model=ExecuteCommandResponse)
async def execute_command(container_id: str, request: ExecuteCommandRequest):
    """Execute a command in the container."""
    try:
        result = await isolator.execute_command(
            container_id=container_id,
            command=request.command,
            working_dir=request.working_dir,
            timeout=request.timeout
        )
        return ExecuteCommandResponse(**result)
    except Exception as e:
        logger.error(f"Failed to execute command: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/containers/{container_id}/files", response_model=FileOperationResponse)
async def file_operation(container_id: str, request: FileOperationRequest):
    """Perform file operations in the container."""
    try:
        result = await isolator.file_operation(
            container_id=container_id,
            operation=request.operation,
            path=request.path,
            content=request.content,
            destination=request.destination
        )
        return FileOperationResponse(**result)
    except Exception as e:
        logger.error(f"Failed to perform file operation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/containers/{container_id}/terminal")
async def terminal_websocket(websocket: WebSocket, container_id: str):
    """WebSocket endpoint for terminal access."""
    await websocket.accept()
    try:
        await isolator.handle_terminal_session(container_id, websocket)
    except WebSocketDisconnect:
        logger.info(f"Terminal session disconnected for container {container_id}")
    except Exception as e:
        logger.error(f"Terminal session error: {e}")
        await websocket.close()

@app.get("/containers")
async def list_containers():
    """List all active containers."""
    try:
        containers = await isolator.list_containers()
        return {"containers": containers}
    except Exception as e:
        logger.error(f"Failed to list containers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("ISOLATOR_PORT", 8001))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )