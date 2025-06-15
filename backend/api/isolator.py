"""
NEO Isolator API

Provides endpoints for managing isolated containers and executing code.
Replaces Daytona API functionality.
"""

from fastapi import APIRouter, HTTPException, status, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import httpx
import logging

from services.auth import auth_service
from utils.config import config

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/isolator", tags=["isolator"])

class CreateContainerRequest(BaseModel):
    image: Optional[str] = "python:3.11-slim"
    workspace_id: Optional[str] = None
    environment: Optional[Dict[str, str]] = None
    memory_limit: Optional[str] = "512m"
    cpu_limit: Optional[float] = 1.0
    timeout: Optional[int] = 3600

class ExecuteCommandRequest(BaseModel):
    command: str
    working_dir: Optional[str] = "/workspace"
    timeout: Optional[int] = 30
    environment: Optional[Dict[str, str]] = None

class FileOperationRequest(BaseModel):
    operation: str  # read, write, delete, list, copy
    path: str
    content: Optional[str] = None
    destination: Optional[str] = None
    encoding: Optional[str] = "utf-8"

class IsolatorClient:
    """Client for communicating with the NEO Isolator service."""
    
    def __init__(self):
        self.base_url = config.ISOLATOR_URL
        self.api_key = config.ISOLATOR_API_KEY
    
    async def _make_request(self, method: str, endpoint: str, **kwargs):
        """Make HTTP request to isolator service."""
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.pop("headers", {})
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(method, url, headers=headers, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Isolator request failed: {e}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Isolator service unavailable"
                )
    
    async def create_container(self, request: CreateContainerRequest) -> Dict[str, Any]:
        """Create a new container."""
        return await self._make_request(
            "POST",
            "/containers",
            json=request.dict()
        )
    
    async def get_container(self, container_id: str) -> Dict[str, Any]:
        """Get container information."""
        return await self._make_request("GET", f"/containers/{container_id}")
    
    async def delete_container(self, container_id: str) -> Dict[str, Any]:
        """Delete a container."""
        return await self._make_request("DELETE", f"/containers/{container_id}")
    
    async def execute_command(
        self,
        container_id: str,
        request: ExecuteCommandRequest
    ) -> Dict[str, Any]:
        """Execute command in container."""
        return await self._make_request(
            "POST",
            f"/containers/{container_id}/execute",
            json=request.dict()
        )
    
    async def file_operation(
        self,
        container_id: str,
        request: FileOperationRequest
    ) -> Dict[str, Any]:
        """Perform file operation in container."""
        return await self._make_request(
            "POST",
            f"/containers/{container_id}/files",
            json=request.dict()
        )
    
    async def list_containers(self) -> Dict[str, Any]:
        """List all containers."""
        return await self._make_request("GET", "/containers")

# Global isolator client
isolator_client = IsolatorClient()

@router.post("/containers")
async def create_container(request: CreateContainerRequest, http_request: Request):
    """Create a new isolated container."""
    # Authenticate user
    user = await auth_service.get_current_user_from_request(http_request)
    
    # Add user context to workspace_id
    if not request.workspace_id:
        import time
        request.workspace_id = f"user_{user['id']}_{int(time.time())}"
    
    return await isolator_client.create_container(request)

@router.get("/containers/{container_id}")
async def get_container(container_id: str, request: Request):
    """Get container information."""
    # Authenticate user
    await auth_service.get_current_user_from_request(request)
    
    return await isolator_client.get_container(container_id)

@router.delete("/containers/{container_id}")
async def delete_container(container_id: str, request: Request):
    """Delete a container."""
    # Authenticate user
    await auth_service.get_current_user_from_request(request)
    
    return await isolator_client.delete_container(container_id)

@router.post("/containers/{container_id}/execute")
async def execute_command(
    container_id: str,
    request: ExecuteCommandRequest,
    http_request: Request
):
    """Execute a command in the container."""
    # Authenticate user
    await auth_service.get_current_user_from_request(http_request)
    
    return await isolator_client.execute_command(container_id, request)

@router.post("/containers/{container_id}/files")
async def file_operation(
    container_id: str,
    request: FileOperationRequest,
    http_request: Request
):
    """Perform file operations in the container."""
    # Authenticate user
    await auth_service.get_current_user_from_request(http_request)
    
    return await isolator_client.file_operation(container_id, request)

@router.get("/containers")
async def list_containers(request: Request):
    """List all active containers."""
    # Authenticate user
    await auth_service.get_current_user_from_request(request)
    
    return await isolator_client.list_containers()

@router.websocket("/containers/{container_id}/terminal")
async def terminal_websocket(websocket: WebSocket, container_id: str):
    """WebSocket endpoint for terminal access."""
    await websocket.accept()
    
    try:
        # TODO: Add authentication for WebSocket connections
        # For now, we'll proxy the connection to the isolator service
        
        import websockets
        import asyncio
        import json
        
        # Connect to isolator WebSocket
        isolator_ws_url = f"ws://{config.ISOLATOR_URL.replace('http://', '')}/containers/{container_id}/terminal"
        
        async with websockets.connect(isolator_ws_url) as isolator_ws:
            # Proxy messages between client and isolator
            async def proxy_to_isolator():
                try:
                    while True:
                        data = await websocket.receive_text()
                        await isolator_ws.send(data)
                except WebSocketDisconnect:
                    pass
            
            async def proxy_from_isolator():
                try:
                    async for message in isolator_ws:
                        await websocket.send_text(message)
                except:
                    pass
            
            # Run both proxy tasks concurrently
            await asyncio.gather(
                proxy_to_isolator(),
                proxy_from_isolator(),
                return_exceptions=True
            )
    
    except Exception as e:
        logger.error(f"Terminal WebSocket error: {e}")
        await websocket.close()

@router.get("/health")
async def health_check():
    """Check isolator service health."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{config.ISOLATOR_URL}/health")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Isolator health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Isolator service unavailable"
        )