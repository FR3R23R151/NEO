"""
Mock sandbox implementation to replace Daytona SDK.
This provides compatibility with the existing sandbox interface.
"""

from dotenv import load_dotenv
from utils.logger import logger
from utils.config import config
import uuid
from typing import Optional, Dict, Any
import asyncio

load_dotenv()

logger.debug("Initializing mock sandbox configuration (Daytona replacement)")

# Mock classes for compatibility
class MockPreviewLink:
    def __init__(self, url: str, token: str = None):
        self.url = url
        self.token = token or "mock-token"

class MockSandbox:
    def __init__(self, sandbox_id: str):
        self.id = sandbox_id
        self.name = f"sandbox-{sandbox_id}"
        self.state = "RUNNING"
        
    def get_preview_link(self, port: int):
        """Get preview link for a port."""
        url = f"http://localhost:{port}/sandbox/{self.id}"
        return MockPreviewLink(url)
        
class MockDaytona:
    def __init__(self, config=None):
        self.config = config
        self._sandboxes = {}
        
    def create_sandbox(self, params):
        sandbox_id = str(uuid.uuid4())[:8]
        sandbox = MockSandbox(sandbox_id)
        self._sandboxes[sandbox_id] = sandbox
        logger.info(f"Mock: Created sandbox {sandbox_id}")
        return sandbox
    
    def get(self, sandbox_id: str):
        logger.info(f"Mock: Getting sandbox {sandbox_id}")
        if sandbox_id in self._sandboxes:
            return self._sandboxes[sandbox_id]
        return MockSandbox(sandbox_id)
    
    def delete(self, sandbox_id: str):
        logger.info(f"Mock: Deleted sandbox {sandbox_id}")
        if sandbox_id in self._sandboxes:
            del self._sandboxes[sandbox_id]
        return True
    
    def execute_command(self, sandbox_id: str, command: str):
        logger.info(f"Mock: Executing command in sandbox {sandbox_id}: {command}")
        return {"output": f"Mock output for: {command}", "exit_code": 0}

# Initialize mock Daytona instance
daytona = MockDaytona()

async def get_or_start_sandbox(sandbox_id: str):
    """Retrieve a sandbox by ID, check its state, and start it if needed."""
    
    logger.info(f"Getting or starting sandbox with ID: {sandbox_id}")
    
    try:
        sandbox = daytona.get(sandbox_id)
        logger.info(f"Mock: Sandbox {sandbox_id} is {sandbox.state}")
        return sandbox
    except Exception as e:
        logger.error(f"Error getting sandbox {sandbox_id}: {e}")
        return None

def create_sandbox(sandbox_pass: str = None, project_id: str = None, **kwargs):
    """Create a new sandbox (sync version for compatibility)."""
    
    logger.info(f"Creating new sandbox for project: {project_id}")
    
    try:
        # Mock parameters
        params = {
            "image": "ubuntu:latest",
            "project_id": project_id,
            **kwargs
        }
        
        sandbox = daytona.create_sandbox(params)
        logger.info(f"Mock: Created sandbox {sandbox.id}")
        return sandbox
    except Exception as e:
        logger.error(f"Error creating sandbox: {e}")
        return None

async def create_sandbox_async(image_name: str = None, **kwargs):
    """Create a new sandbox (async version)."""
    
    logger.info(f"Creating new sandbox with image: {image_name}")
    
    try:
        # Mock parameters
        params = {
            "image": image_name or "ubuntu:latest",
            **kwargs
        }
        
        sandbox = daytona.create_sandbox(params)
        logger.info(f"Mock: Created sandbox {sandbox.id}")
        return sandbox
    except Exception as e:
        logger.error(f"Error creating sandbox: {e}")
        return None

async def delete_sandbox(sandbox_id: str):
    """Delete a sandbox."""
    
    logger.info(f"Deleting sandbox with ID: {sandbox_id}")
    
    try:
        result = daytona.delete(sandbox_id)
        logger.info(f"Mock: Deleted sandbox {sandbox_id}")
        return result
    except Exception as e:
        logger.error(f"Error deleting sandbox {sandbox_id}: {e}")
        return False

async def execute_command_in_sandbox(sandbox_id: str, command: str):
    """Execute a command in a sandbox."""
    
    logger.info(f"Executing command in sandbox {sandbox_id}: {command}")
    
    try:
        result = daytona.execute_command(sandbox_id, command)
        logger.info(f"Mock: Command executed in sandbox {sandbox_id}")
        return result
    except Exception as e:
        logger.error(f"Error executing command in sandbox {sandbox_id}: {e}")
        return {"output": "", "exit_code": 1, "error": str(e)}