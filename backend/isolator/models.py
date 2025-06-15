"""
Pydantic models for the NEO Isolator Service.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class CreateContainerRequest(BaseModel):
    """Request model for creating a container."""
    image: str = Field(default="python:3.11-slim", description="Docker image to use")
    workspace_id: str = Field(..., description="Unique workspace identifier")
    environment: Optional[Dict[str, str]] = Field(default=None, description="Environment variables")
    memory_limit: Optional[str] = Field(default="512m", description="Memory limit")
    cpu_limit: Optional[float] = Field(default=1.0, description="CPU limit")
    timeout: Optional[int] = Field(default=3600, description="Container timeout in seconds")

class ContainerResponse(BaseModel):
    """Response model for container operations."""
    container_id: str
    status: str
    workspace_id: str
    created_at: Optional[str] = None
    image: Optional[str] = None

class ExecuteCommandRequest(BaseModel):
    """Request model for executing commands."""
    command: str = Field(..., description="Command to execute")
    working_dir: Optional[str] = Field(default="/workspace", description="Working directory")
    timeout: Optional[int] = Field(default=30, description="Command timeout in seconds")
    environment: Optional[Dict[str, str]] = Field(default=None, description="Additional environment variables")

class ExecuteCommandResponse(BaseModel):
    """Response model for command execution."""
    exit_code: int
    stdout: str
    stderr: str
    execution_time: float

class FileOperationRequest(BaseModel):
    """Request model for file operations."""
    operation: str = Field(..., description="Operation type: read, write, delete, list, copy")
    path: str = Field(..., description="File or directory path")
    content: Optional[str] = Field(default=None, description="Content for write operations")
    destination: Optional[str] = Field(default=None, description="Destination for copy operations")
    encoding: Optional[str] = Field(default="utf-8", description="File encoding")

class FileOperationResponse(BaseModel):
    """Response model for file operations."""
    success: bool
    content: Optional[str] = None
    files: Optional[List[str]] = None
    message: Optional[str] = None

class ContainerStats(BaseModel):
    """Container resource usage statistics."""
    cpu_percent: float
    memory_usage: int
    memory_limit: int
    memory_percent: float
    network_rx: int
    network_tx: int

class WorkspaceInfo(BaseModel):
    """Workspace information."""
    workspace_id: str
    container_id: Optional[str] = None
    status: str
    created_at: str
    last_activity: Optional[str] = None
    stats: Optional[ContainerStats] = None