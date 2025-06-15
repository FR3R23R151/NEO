"""
NEO Isolator - Custom container isolation service.

This module provides secure container isolation for executing agent code,
replacing Daytona with a custom Docker-based solution.
"""

import os
import asyncio
import time
import json
import logging
import tempfile
import shutil
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import docker
from docker.errors import DockerException, NotFound, APIError
from fastapi import WebSocket
import aiofiles

logger = logging.getLogger(__name__)

class NEOIsolator:
    """
    NEO Isolator provides secure container isolation for agent execution.
    """
    
    def __init__(self):
        self.docker_client = None
        self.containers: Dict[str, Dict[str, Any]] = {}
        self.workspace_dir = os.getenv("WORKSPACE_DIR", "/app/workspaces")
        self.default_image = "python:3.11-slim"
        self.network_name = "neo_isolator_network"
        
    async def initialize(self):
        """Initialize the isolator service."""
        try:
            # Initialize Docker client
            self.docker_client = docker.from_env()
            
            # Test Docker connection
            self.docker_client.ping()
            logger.info("Docker connection established")
            
            # Create workspace directory
            os.makedirs(self.workspace_dir, exist_ok=True)
            
            # Create isolated network
            await self._create_network()
            
            # Pull default image
            await self._pull_image(self.default_image)
            
            logger.info("NEO Isolator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize NEO Isolator: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            # Stop and remove all containers
            for container_id in list(self.containers.keys()):
                await self.delete_container(container_id)
            
            # Remove network
            await self._remove_network()
            
            if self.docker_client:
                self.docker_client.close()
                
            logger.info("NEO Isolator cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def create_container(
        self,
        image: str = None,
        workspace_id: str = None,
        environment: Dict[str, str] = None,
        memory_limit: str = "512m",
        cpu_limit: float = 1.0,
        timeout: int = 3600
    ) -> str:
        """Create a new isolated container."""
        try:
            if not image:
                image = self.default_image
            
            if not workspace_id:
                workspace_id = f"workspace_{int(time.time())}"
            
            # Create workspace directory
            workspace_path = os.path.join(self.workspace_dir, workspace_id)
            os.makedirs(workspace_path, exist_ok=True)
            
            # Prepare environment variables
            env_vars = {
                "WORKSPACE_ID": workspace_id,
                "PYTHONUNBUFFERED": "1",
                "DEBIAN_FRONTEND": "noninteractive"
            }
            if environment:
                env_vars.update(environment)
            
            # Pull image if not exists
            await self._pull_image(image)
            
            # Create container
            container = self.docker_client.containers.run(
                image=image,
                detach=True,
                environment=env_vars,
                volumes={
                    workspace_path: {"bind": "/workspace", "mode": "rw"}
                },
                working_dir="/workspace",
                mem_limit=memory_limit,
                cpu_quota=int(cpu_limit * 100000),
                cpu_period=100000,
                network=self.network_name,
                security_opt=["no-new-privileges:true"],
                cap_drop=["ALL"],
                cap_add=["CHOWN", "DAC_OVERRIDE", "FOWNER", "SETGID", "SETUID"],
                read_only=False,
                tmpfs={"/tmp": "noexec,nosuid,size=100m"},
                command="tail -f /dev/null"  # Keep container running
            )
            
            container_id = container.id
            
            # Store container info
            self.containers[container_id] = {
                "container_id": container_id,
                "workspace_id": workspace_id,
                "image": image,
                "status": "running",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "workspace_path": workspace_path,
                "timeout": timeout,
                "last_activity": time.time()
            }
            
            # Install basic tools in container
            await self._setup_container(container_id)
            
            logger.info(f"Container {container_id} created for workspace {workspace_id}")
            return container_id
            
        except Exception as e:
            logger.error(f"Failed to create container: {e}")
            raise
    
    async def delete_container(self, container_id: str):
        """Delete a container and cleanup resources."""
        try:
            if container_id not in self.containers:
                raise ValueError(f"Container {container_id} not found")
            
            container_info = self.containers[container_id]
            
            # Stop and remove container
            try:
                container = self.docker_client.containers.get(container_id)
                container.stop(timeout=10)
                container.remove()
            except NotFound:
                logger.warning(f"Container {container_id} not found in Docker")
            
            # Cleanup workspace directory
            workspace_path = container_info.get("workspace_path")
            if workspace_path and os.path.exists(workspace_path):
                shutil.rmtree(workspace_path, ignore_errors=True)
            
            # Remove from tracking
            del self.containers[container_id]
            
            logger.info(f"Container {container_id} deleted")
            
        except Exception as e:
            logger.error(f"Failed to delete container {container_id}: {e}")
            raise
    
    async def execute_command(
        self,
        container_id: str,
        command: str,
        working_dir: str = "/workspace",
        timeout: int = 30,
        environment: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """Execute a command in the container."""
        try:
            if container_id not in self.containers:
                raise ValueError(f"Container {container_id} not found")
            
            container = self.docker_client.containers.get(container_id)
            
            # Update last activity
            self.containers[container_id]["last_activity"] = time.time()
            
            # Prepare environment
            env_vars = {}
            if environment:
                env_vars.update(environment)
            
            start_time = time.time()
            
            # Execute command
            exec_result = container.exec_run(
                cmd=command,
                workdir=working_dir,
                environment=env_vars,
                demux=True,
                tty=False
            )
            
            execution_time = time.time() - start_time
            
            # Process output
            stdout = exec_result.output[0].decode('utf-8') if exec_result.output[0] else ""
            stderr = exec_result.output[1].decode('utf-8') if exec_result.output[1] else ""
            
            result = {
                "exit_code": exec_result.exit_code,
                "stdout": stdout,
                "stderr": stderr,
                "execution_time": execution_time
            }
            
            logger.info(f"Command executed in {container_id}: {command[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute command in {container_id}: {e}")
            raise
    
    async def file_operation(
        self,
        container_id: str,
        operation: str,
        path: str,
        content: str = None,
        destination: str = None
    ) -> Dict[str, Any]:
        """Perform file operations in the container."""
        try:
            if container_id not in self.containers:
                raise ValueError(f"Container {container_id} not found")
            
            workspace_path = self.containers[container_id]["workspace_path"]
            full_path = os.path.join(workspace_path, path.lstrip('/'))
            
            # Update last activity
            self.containers[container_id]["last_activity"] = time.time()
            
            if operation == "read":
                if not os.path.exists(full_path):
                    raise FileNotFoundError(f"File {path} not found")
                
                async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                
                return {"success": True, "content": content}
            
            elif operation == "write":
                if content is None:
                    raise ValueError("Content is required for write operation")
                
                # Create directory if needed
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                async with aiofiles.open(full_path, 'w', encoding='utf-8') as f:
                    await f.write(content)
                
                return {"success": True, "message": f"File {path} written successfully"}
            
            elif operation == "delete":
                if os.path.exists(full_path):
                    if os.path.isfile(full_path):
                        os.remove(full_path)
                    else:
                        shutil.rmtree(full_path)
                
                return {"success": True, "message": f"Path {path} deleted successfully"}
            
            elif operation == "list":
                if not os.path.exists(full_path):
                    return {"success": True, "files": []}
                
                if os.path.isfile(full_path):
                    return {"success": True, "files": [os.path.basename(full_path)]}
                
                files = os.listdir(full_path)
                return {"success": True, "files": files}
            
            elif operation == "copy":
                if destination is None:
                    raise ValueError("Destination is required for copy operation")
                
                dest_path = os.path.join(workspace_path, destination.lstrip('/'))
                
                if os.path.isfile(full_path):
                    shutil.copy2(full_path, dest_path)
                else:
                    shutil.copytree(full_path, dest_path)
                
                return {"success": True, "message": f"Copied {path} to {destination}"}
            
            else:
                raise ValueError(f"Unknown operation: {operation}")
                
        except Exception as e:
            logger.error(f"File operation failed: {e}")
            return {"success": False, "message": str(e)}
    
    async def get_container_info(self, container_id: str) -> Dict[str, Any]:
        """Get container information."""
        if container_id not in self.containers:
            raise ValueError(f"Container {container_id} not found")
        
        container_info = self.containers[container_id].copy()
        
        # Get current status from Docker
        try:
            container = self.docker_client.containers.get(container_id)
            container_info["status"] = container.status
        except NotFound:
            container_info["status"] = "not_found"
        
        return container_info
    
    async def list_containers(self) -> List[Dict[str, Any]]:
        """List all active containers."""
        containers = []
        for container_id, info in self.containers.items():
            try:
                container = self.docker_client.containers.get(container_id)
                info_copy = info.copy()
                info_copy["status"] = container.status
                containers.append(info_copy)
            except NotFound:
                info_copy = info.copy()
                info_copy["status"] = "not_found"
                containers.append(info_copy)
        
        return containers
    
    async def handle_terminal_session(self, container_id: str, websocket: WebSocket):
        """Handle WebSocket terminal session."""
        if container_id not in self.containers:
            await websocket.send_text(json.dumps({"error": "Container not found"}))
            return
        
        try:
            container = self.docker_client.containers.get(container_id)
            
            # Create exec instance for shell
            exec_instance = container.exec_run(
                cmd="/bin/bash",
                stdin=True,
                tty=True,
                socket=True
            )
            
            # Handle WebSocket communication
            while True:
                try:
                    # Receive data from WebSocket
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    if message.get("type") == "input":
                        # Send input to container
                        exec_instance.socket.send(message.get("data", "").encode())
                    
                    # Read output from container (non-blocking)
                    try:
                        output = exec_instance.socket.recv(1024, socket.MSG_DONTWAIT)
                        if output:
                            await websocket.send_text(json.dumps({
                                "type": "output",
                                "data": output.decode('utf-8', errors='ignore')
                            }))
                    except BlockingIOError:
                        pass
                    
                except Exception as e:
                    logger.error(f"Terminal session error: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Failed to create terminal session: {e}")
            await websocket.send_text(json.dumps({"error": str(e)}))
    
    async def _create_network(self):
        """Create isolated Docker network."""
        try:
            # Check if network exists
            networks = self.docker_client.networks.list(names=[self.network_name])
            if networks:
                logger.info(f"Network {self.network_name} already exists")
                return
            
            # Create network
            self.docker_client.networks.create(
                name=self.network_name,
                driver="bridge",
                options={
                    "com.docker.network.bridge.enable_icc": "false",
                    "com.docker.network.bridge.enable_ip_masquerade": "true"
                }
            )
            logger.info(f"Created network {self.network_name}")
            
        except Exception as e:
            logger.error(f"Failed to create network: {e}")
            raise
    
    async def _remove_network(self):
        """Remove isolated Docker network."""
        try:
            networks = self.docker_client.networks.list(names=[self.network_name])
            if networks:
                networks[0].remove()
                logger.info(f"Removed network {self.network_name}")
        except Exception as e:
            logger.warning(f"Failed to remove network: {e}")
    
    async def _pull_image(self, image: str):
        """Pull Docker image if not exists."""
        try:
            # Check if image exists locally
            try:
                self.docker_client.images.get(image)
                logger.info(f"Image {image} already exists locally")
                return
            except NotFound:
                pass
            
            # Pull image
            logger.info(f"Pulling image {image}...")
            self.docker_client.images.pull(image)
            logger.info(f"Image {image} pulled successfully")
            
        except Exception as e:
            logger.error(f"Failed to pull image {image}: {e}")
            raise
    
    async def _setup_container(self, container_id: str):
        """Setup basic tools in the container."""
        try:
            # Install basic packages
            setup_commands = [
                "apt-get update",
                "apt-get install -y curl wget git nano vim",
                "pip install --upgrade pip",
                "pip install requests beautifulsoup4 pandas numpy matplotlib seaborn"
            ]
            
            for cmd in setup_commands:
                try:
                    await self.execute_command(
                        container_id=container_id,
                        command=cmd,
                        timeout=60
                    )
                except Exception as e:
                    logger.warning(f"Setup command failed: {cmd} - {e}")
            
            logger.info(f"Container {container_id} setup completed")
            
        except Exception as e:
            logger.warning(f"Container setup failed: {e}")