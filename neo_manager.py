#!/usr/bin/env python3
"""
Enhanced NEO Service Management Script

This script provides comprehensive management for all NEO services with enhanced features:
- Intelligent service dependency management
- Health monitoring and auto-recovery
- Cross-platform support (Windows, Linux, macOS)
- Enhanced logging and diagnostics
- Performance monitoring
- Automatic error recovery
- Service orchestration

Services managed:
- PostgreSQL database
- Redis cache
- MinIO object storage  
- RabbitMQ message queue
- NEO Isolator service
- NEO Backend API
- NEO Worker processes
- NEO Frontend

Usage:
    python neo_manager.py start [--dev] [--logs] [--profile PROFILE]
    python neo_manager.py stop [--force]
    python neo_manager.py restart [--service SERVICE]
    python neo_manager.py status [--detailed]
    python neo_manager.py logs [--follow] [--service SERVICE] [--lines N]
    python neo_manager.py health [--fix]
    python neo_manager.py setup [--reset]
    python neo_manager.py monitor [--interval SECONDS]
    python neo_manager.py backup [--type TYPE]
    python neo_manager.py restore [--file FILE]
"""

import argparse
import asyncio
import json
import os
import platform
import subprocess
import sys
import time
import signal
import threading
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import yaml
from dataclasses import dataclass
from enum import Enum

try:
    import psutil
    import requests
    ENHANCED_FEATURES = True
except ImportError:
    ENHANCED_FEATURES = False
    print("⚠️ Enhanced features disabled. Install psutil and requests for full functionality:")
    print("   pip install psutil requests")

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class ServiceStatus(Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    STARTING = "starting"
    STOPPING = "stopping"
    ERROR = "error"
    UNKNOWN = "unknown"

@dataclass
class ServiceInfo:
    name: str
    port: int
    health_endpoint: Optional[str] = None
    dependencies: List[str] = None
    startup_time: int = 30  # seconds
    critical: bool = True
    docker_service: bool = True
    process_name: Optional[str] = None
    command: Optional[str] = None
    working_dir: Optional[str] = None

def print_colored(message: str, color: str = Colors.ENDC):
    """Print colored message to terminal."""
    print(f"{color}{message}{Colors.ENDC}")

def print_header(message: str):
    """Print header message."""
    print_colored(f"\n{'='*60}", Colors.HEADER)
    print_colored(f"  {message}", Colors.HEADER)
    print_colored(f"{'='*60}", Colors.HEADER)

def print_success(message: str):
    """Print success message."""
    print_colored(f"✅ {message}", Colors.OKGREEN)

def print_warning(message: str):
    """Print warning message."""
    print_colored(f"⚠️  {message}", Colors.WARNING)

def print_error(message: str):
    """Print error message."""
    print_colored(f"❌ {message}", Colors.FAIL)

def print_info(message: str):
    """Print info message."""
    print_colored(f"ℹ️  {message}", Colors.OKBLUE)

class NEOManager:
    """Enhanced NEO service manager with intelligent orchestration."""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.is_windows = platform.system() == "Windows"
        self.is_macos = platform.system() == "Darwin"
        self.is_linux = platform.system() == "Linux"
        
        # Service definitions with enhanced metadata
        self.services = {
            "postgres": ServiceInfo(
                name="postgres",
                port=5432,
                health_endpoint="tcp://localhost:5432",
                dependencies=[],
                startup_time=15,
                critical=True,
                docker_service=True
            ),
            "redis": ServiceInfo(
                name="redis",
                port=6379,
                health_endpoint="tcp://localhost:6379",
                dependencies=[],
                startup_time=10,
                critical=True,
                docker_service=True
            ),
            "minio": ServiceInfo(
                name="minio",
                port=9000,
                health_endpoint="http://localhost:9000/minio/health/live",
                dependencies=[],
                startup_time=15,
                critical=True,
                docker_service=True
            ),
            "rabbitmq": ServiceInfo(
                name="rabbitmq",
                port=5672,
                health_endpoint="http://localhost:15672/api/healthchecks/node",
                dependencies=[],
                startup_time=20,
                critical=True,
                docker_service=True
            ),
            "isolator": ServiceInfo(
                name="isolator",
                port=8001,
                health_endpoint="http://localhost:8001/health",
                dependencies=["postgres", "redis"],
                startup_time=30,
                critical=True,
                docker_service=False,
                process_name="python",
                command="poetry run python -m isolator.main",
                working_dir="backend"
            ),
            "backend": ServiceInfo(
                name="backend",
                port=8000,
                health_endpoint="http://localhost:8000/health",
                dependencies=["postgres", "redis", "minio", "rabbitmq"],
                startup_time=45,
                critical=True,
                docker_service=False,
                process_name="python",
                command="poetry run python api_new.py",
                working_dir="backend"
            ),
            "worker": ServiceInfo(
                name="worker",
                port=0,  # No port for worker
                dependencies=["postgres", "redis", "rabbitmq"],
                startup_time=30,
                critical=False,
                docker_service=False,
                process_name="python",
                command="poetry run python -m celery worker",
                working_dir="backend"
            ),
            "frontend": ServiceInfo(
                name="frontend",
                port=3000,
                health_endpoint="http://localhost:3000/api/health",
                dependencies=["backend"],
                startup_time=60,
                critical=True,
                docker_service=False,
                process_name="node",
                command="npm run dev",
                working_dir="frontend"
            )
        }
        
        self.running_processes = {}
        self.monitoring = False
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration."""
        log_dir = self.root_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "neo_manager.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("NEOManager")
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are installed."""
        print_header("Checking Prerequisites")
        
        prerequisites = {
            "docker": ["docker", "--version"],
            "docker-compose": ["docker-compose", "--version"],
            "python": ["python", "--version"],
            "node": ["node", "--version"],
            "npm": ["npm", "--version"]
        }
        
        if self.is_windows:
            prerequisites["poetry"] = ["poetry", "--version"]
        
        all_good = True
        
        for name, command in prerequisites.items():
            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    check=True
                )
                version = result.stdout.strip().split('\n')[0]
                print_success(f"{name}: {version}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print_error(f"{name}: Not found or not working")
                all_good = False
        
        # Check Docker daemon
        try:
            subprocess.run(["docker", "info"], capture_output=True, check=True)
            print_success("Docker daemon: Running")
        except subprocess.CalledProcessError:
            print_error("Docker daemon: Not running")
            all_good = False
        
        return all_good
    
    def check_service_health(self, service_name: str) -> ServiceStatus:
        """Check health of a specific service."""
        service = self.services.get(service_name)
        if not service:
            return ServiceStatus.UNKNOWN
        
        try:
            if service.docker_service:
                # Check Docker container status
                result = subprocess.run(
                    ["docker-compose", "ps", "-q", service_name],
                    capture_output=True,
                    text=True,
                    cwd=self.root_dir
                )
                
                if not result.stdout.strip():
                    return ServiceStatus.STOPPED
                
                # Check if container is running
                container_id = result.stdout.strip()
                result = subprocess.run(
                    ["docker", "inspect", "--format", "{{.State.Status}}", container_id],
                    capture_output=True,
                    text=True
                )
                
                status = result.stdout.strip()
                if status == "running":
                    # Additional health check via endpoint
                    if service.health_endpoint and ENHANCED_FEATURES:
                        return self._check_endpoint_health(service.health_endpoint)
                    return ServiceStatus.RUNNING
                elif status in ["created", "restarting"]:
                    return ServiceStatus.STARTING
                elif status in ["paused", "exited", "dead"]:
                    return ServiceStatus.STOPPED
                else:
                    return ServiceStatus.ERROR
            
            else:
                # Check process-based service
                if ENHANCED_FEATURES:
                    return self._check_process_health(service)
                else:
                    # Fallback: check port
                    if service.port > 0:
                        return self._check_port_health(service.port)
                    return ServiceStatus.UNKNOWN
        
        except Exception as e:
            self.logger.error(f"Error checking health for {service_name}: {e}")
            return ServiceStatus.ERROR
    
    def _check_endpoint_health(self, endpoint: str) -> ServiceStatus:
        """Check service health via HTTP endpoint."""
        try:
            if endpoint.startswith("http"):
                response = requests.get(endpoint, timeout=5)
                if response.status_code == 200:
                    return ServiceStatus.RUNNING
                else:
                    return ServiceStatus.ERROR
            elif endpoint.startswith("tcp"):
                # TCP health check
                import socket
                host, port = endpoint.replace("tcp://", "").split(":")
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((host, int(port)))
                sock.close()
                return ServiceStatus.RUNNING if result == 0 else ServiceStatus.ERROR
        except Exception:
            return ServiceStatus.ERROR
    
    def _check_process_health(self, service: ServiceInfo) -> ServiceStatus:
        """Check process-based service health."""
        try:
            # Check if process is running
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if service.process_name in proc.info['name']:
                        cmdline = ' '.join(proc.info['cmdline'])
                        if service.name in cmdline or (service.command and service.command in cmdline):
                            # Process found, check if port is listening (if applicable)
                            if service.port > 0:
                                return self._check_port_health(service.port)
                            return ServiceStatus.RUNNING
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return ServiceStatus.STOPPED
        except Exception:
            return ServiceStatus.UNKNOWN
    
    def _check_port_health(self, port: int) -> ServiceStatus:
        """Check if port is listening."""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return ServiceStatus.RUNNING if result == 0 else ServiceStatus.STOPPED
        except Exception:
            return ServiceStatus.UNKNOWN
    
    def start_docker_services(self) -> bool:
        """Start Docker-based services."""
        print_header("Starting Docker Services")
        
        docker_services = [name for name, service in self.services.items() if service.docker_service]
        
        try:
            # Start Docker services
            cmd = ["docker-compose", "up", "-d"] + docker_services
            result = subprocess.run(cmd, cwd=self.root_dir, check=True)
            
            print_success("Docker services started")
            
            # Wait for services to be ready
            print_info("Waiting for Docker services to be ready...")
            for service_name in docker_services:
                service = self.services[service_name]
                self._wait_for_service(service_name, service.startup_time)
            
            return True
            
        except subprocess.CalledProcessError as e:
            print_error(f"Failed to start Docker services: {e}")
            return False
    
    def start_process_services(self, dev_mode: bool = False) -> bool:
        """Start process-based services."""
        print_header("Starting Process Services")
        
        process_services = [name for name, service in self.services.items() if not service.docker_service]
        
        # Start services in dependency order
        for service_name in process_services:
            service = self.services[service_name]
            
            # Check dependencies
            for dep in service.dependencies or []:
                if self.check_service_health(dep) != ServiceStatus.RUNNING:
                    print_error(f"Dependency {dep} not running for {service_name}")
                    return False
            
            # Start service
            if not self._start_process_service(service_name, dev_mode):
                print_error(f"Failed to start {service_name}")
                return False
        
        return True
    
    def _start_process_service(self, service_name: str, dev_mode: bool = False) -> bool:
        """Start a single process service."""
        service = self.services[service_name]
        
        if not service.command:
            print_warning(f"No command defined for {service_name}")
            return True
        
        print_info(f"Starting {service_name}...")
        
        try:
            working_dir = self.root_dir / service.working_dir if service.working_dir else self.root_dir
            
            # Prepare environment
            env = os.environ.copy()
            if dev_mode:
                env["NODE_ENV"] = "development"
                env["PYTHON_ENV"] = "development"
            
            # Start process
            if self.is_windows:
                # Windows: start in new window
                cmd = f'start "NEO {service_name}" cmd /k "{service.command}"'
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    cwd=working_dir,
                    env=env
                )
            else:
                # Unix: start in background
                process = subprocess.Popen(
                    service.command,
                    shell=True,
                    cwd=working_dir,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            self.running_processes[service_name] = process
            
            # Wait for service to be ready
            self._wait_for_service(service_name, service.startup_time)
            
            print_success(f"{service_name} started successfully")
            return True
            
        except Exception as e:
            print_error(f"Failed to start {service_name}: {e}")
            return False
    
    def _wait_for_service(self, service_name: str, timeout: int):
        """Wait for service to be ready."""
        service = self.services[service_name]
        start_time = time.time()
        
        print_info(f"Waiting for {service_name} to be ready (timeout: {timeout}s)...")
        
        while time.time() - start_time < timeout:
            status = self.check_service_health(service_name)
            if status == ServiceStatus.RUNNING:
                print_success(f"{service_name} is ready")
                return True
            elif status == ServiceStatus.ERROR:
                print_warning(f"{service_name} has errors, continuing...")
                return False
            
            time.sleep(2)
        
        print_warning(f"{service_name} not ready after {timeout}s")
        return False
    
    def stop_services(self, force: bool = False) -> bool:
        """Stop all services."""
        print_header("Stopping NEO Services")
        
        success = True
        
        # Stop process services first
        for service_name, process in self.running_processes.items():
            try:
                if self.is_windows:
                    # Windows: terminate process tree
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)], 
                                 capture_output=True)
                else:
                    # Unix: send SIGTERM, then SIGKILL if needed
                    process.terminate()
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        if force:
                            process.kill()
                
                print_success(f"Stopped {service_name}")
            except Exception as e:
                print_error(f"Failed to stop {service_name}: {e}")
                success = False
        
        self.running_processes.clear()
        
        # Stop Docker services
        try:
            cmd = ["docker-compose", "down"]
            if force:
                cmd.extend(["--remove-orphans", "--volumes"])
            
            subprocess.run(cmd, cwd=self.root_dir, check=True)
            print_success("Docker services stopped")
        except subprocess.CalledProcessError as e:
            print_error(f"Failed to stop Docker services: {e}")
            success = False
        
        return success
    
    def get_status(self, detailed: bool = False) -> Dict[str, Any]:
        """Get status of all services."""
        status = {}
        
        for service_name, service in self.services.items():
            service_status = self.check_service_health(service_name)
            
            status[service_name] = {
                "status": service_status.value,
                "port": service.port if service.port > 0 else None,
                "critical": service.critical,
                "docker": service.docker_service
            }
            
            if detailed and ENHANCED_FEATURES:
                # Add detailed information
                if service.docker_service:
                    status[service_name].update(self._get_docker_details(service_name))
                else:
                    status[service_name].update(self._get_process_details(service_name))
        
        return status
    
    def _get_docker_details(self, service_name: str) -> Dict[str, Any]:
        """Get detailed Docker service information."""
        try:
            result = subprocess.run(
                ["docker-compose", "ps", "--format", "json", service_name],
                capture_output=True,
                text=True,
                cwd=self.root_dir
            )
            
            if result.stdout:
                return json.loads(result.stdout)
        except Exception:
            pass
        
        return {}
    
    def _get_process_details(self, service_name: str) -> Dict[str, Any]:
        """Get detailed process information."""
        if not ENHANCED_FEATURES:
            return {}
        
        service = self.services[service_name]
        details = {}
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                if service.process_name in proc.info['name']:
                    details.update({
                        "pid": proc.info['pid'],
                        "cpu_percent": proc.info['cpu_percent'],
                        "memory_mb": proc.info['memory_info'].rss / 1024 / 1024
                    })
                    break
        except Exception:
            pass
        
        return details
    
    def print_status(self, detailed: bool = False):
        """Print service status in a formatted way."""
        print_header("NEO Service Status")
        
        status = self.get_status(detailed)
        
        # Print summary
        running_count = sum(1 for s in status.values() if s["status"] == "running")
        total_count = len(status)
        
        if running_count == total_count:
            print_success(f"All services running ({running_count}/{total_count})")
        else:
            print_warning(f"Services running: {running_count}/{total_count}")
        
        print()
        
        # Print detailed status
        for service_name, info in status.items():
            status_color = Colors.OKGREEN if info["status"] == "running" else Colors.FAIL
            critical_marker = "🔴" if info["critical"] else "🟡"
            docker_marker = "🐳" if info["docker"] else "⚙️"
            
            port_info = f":{info['port']}" if info["port"] else ""
            
            print_colored(
                f"{critical_marker} {docker_marker} {service_name}{port_info} - {info['status']}",
                status_color
            )
            
            if detailed and "pid" in info:
                print(f"    PID: {info['pid']}, CPU: {info.get('cpu_percent', 0):.1f}%, "
                      f"Memory: {info.get('memory_mb', 0):.1f}MB")
        
        print()
        
        # Print access URLs
        print_info("Access URLs:")
        urls = {
            "NEO Web Interface": "http://localhost:3000",
            "Backend API": "http://localhost:8000",
            "API Documentation": "http://localhost:8000/docs",
            "Isolator Service": "http://localhost:8001",
            "MinIO Console": "http://localhost:9001",
            "RabbitMQ Management": "http://localhost:15672"
        }
        
        for name, url in urls.items():
            print(f"  • {name}: {url}")
    
    def monitor_services(self, interval: int = 30):
        """Monitor services continuously."""
        print_header(f"Monitoring NEO Services (interval: {interval}s)")
        print("Press Ctrl+C to stop monitoring")
        
        self.monitoring = True
        
        try:
            while self.monitoring:
                os.system('clear' if not self.is_windows else 'cls')
                print_colored(f"NEO Service Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", Colors.HEADER)
                print()
                
                self.print_status(detailed=True)
                
                # Check for issues
                status = self.get_status()
                issues = [name for name, info in status.items() 
                         if info["critical"] and info["status"] != "running"]
                
                if issues:
                    print_warning(f"Critical services with issues: {', '.join(issues)}")
                    print_info("Run 'python neo_manager.py health --fix' to attempt auto-recovery")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.monitoring = False
            print_info("Monitoring stopped")
    
    def health_check(self, fix_issues: bool = False) -> bool:
        """Perform comprehensive health check."""
        print_header("NEO Health Check")
        
        all_healthy = True
        issues = []
        
        # Check prerequisites
        if not self.check_prerequisites():
            issues.append("Prerequisites not met")
            all_healthy = False
        
        # Check services
        status = self.get_status(detailed=True)
        for service_name, info in status.items():
            if info["critical"] and info["status"] != "running":
                issues.append(f"{service_name} not running")
                all_healthy = False
        
        # Check disk space
        if ENHANCED_FEATURES:
            disk_usage = psutil.disk_usage(str(self.root_dir))
            free_gb = disk_usage.free / (1024**3)
            if free_gb < 1:  # Less than 1GB free
                issues.append(f"Low disk space: {free_gb:.1f}GB free")
                all_healthy = False
        
        # Check memory usage
        if ENHANCED_FEATURES:
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                issues.append(f"High memory usage: {memory.percent:.1f}%")
                all_healthy = False
        
        # Report results
        if all_healthy:
            print_success("All health checks passed")
        else:
            print_warning("Health issues detected:")
            for issue in issues:
                print_error(f"  • {issue}")
            
            if fix_issues:
                print_info("Attempting to fix issues...")
                return self._fix_health_issues(issues)
        
        return all_healthy
    
    def _fix_health_issues(self, issues: List[str]) -> bool:
        """Attempt to fix health issues automatically."""
        fixed = 0
        
        for issue in issues:
            if "not running" in issue:
                service_name = issue.split()[0]
                print_info(f"Attempting to restart {service_name}...")
                
                if self.services[service_name].docker_service:
                    try:
                        subprocess.run(
                            ["docker-compose", "restart", service_name],
                            cwd=self.root_dir,
                            check=True
                        )
                        fixed += 1
                        print_success(f"Restarted {service_name}")
                    except subprocess.CalledProcessError:
                        print_error(f"Failed to restart {service_name}")
                else:
                    # Restart process service
                    if self._start_process_service(service_name):
                        fixed += 1
        
        print_info(f"Fixed {fixed}/{len(issues)} issues")
        return fixed == len(issues)
    
    def setup_environment(self, reset: bool = False):
        """Setup NEO environment."""
        print_header("Setting up NEO Environment")
        
        # Create necessary directories
        dirs_to_create = [
            "logs",
            "data",
            "backups",
            "backend/logs",
            "frontend/.next"
        ]
        
        for dir_path in dirs_to_create:
            full_path = self.root_dir / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            print_success(f"Created directory: {dir_path}")
        
        # Setup environment files
        self._setup_env_files(reset)
        
        # Install dependencies
        self._install_dependencies()
        
        print_success("Environment setup completed")
    
    def _setup_env_files(self, reset: bool = False):
        """Setup environment configuration files."""
        env_files = {
            "backend/.env": "backend/.env.example",
            "frontend/.env.local": None  # Custom frontend env
        }
        
        for env_file, example_file in env_files.items():
            env_path = self.root_dir / env_file
            
            if env_path.exists() and not reset:
                print_info(f"Environment file exists: {env_file}")
                continue
            
            if example_file:
                example_path = self.root_dir / example_file
                if example_path.exists():
                    import shutil
                    shutil.copy2(example_path, env_path)
                    print_success(f"Created {env_file} from {example_file}")
            else:
                # Create custom frontend .env.local
                frontend_env = """NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ISOLATOR_URL=http://localhost:8001
NEXT_PUBLIC_MINIO_URL=http://localhost:9000
"""
                env_path.write_text(frontend_env)
                print_success(f"Created {env_file}")
    
    def _install_dependencies(self):
        """Install project dependencies."""
        print_info("Installing dependencies...")
        
        # Backend dependencies
        backend_dir = self.root_dir / "backend"
        if (backend_dir / "pyproject.toml").exists():
            try:
                subprocess.run(
                    ["poetry", "install"],
                    cwd=backend_dir,
                    check=True
                )
                print_success("Backend dependencies installed")
            except subprocess.CalledProcessError:
                print_error("Failed to install backend dependencies")
        
        # Frontend dependencies
        frontend_dir = self.root_dir / "frontend"
        if (frontend_dir / "package.json").exists():
            try:
                subprocess.run(
                    ["npm", "install"],
                    cwd=frontend_dir,
                    check=True
                )
                print_success("Frontend dependencies installed")
            except subprocess.CalledProcessError:
                print_error("Failed to install frontend dependencies")
    
    def backup_data(self, backup_type: str = "full"):
        """Create backup of NEO data."""
        print_header(f"Creating {backup_type} backup")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.root_dir / "backups" / f"neo_backup_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        if backup_type in ["full", "database"]:
            self._backup_database(backup_dir)
        
        if backup_type in ["full", "files"]:
            self._backup_files(backup_dir)
        
        print_success(f"Backup created: {backup_dir}")
    
    def _backup_database(self, backup_dir: Path):
        """Backup PostgreSQL database."""
        try:
            backup_file = backup_dir / "database.sql"
            cmd = [
                "docker-compose", "exec", "-T", "postgres",
                "pg_dumpall", "-U", "neo_user"
            ]
            
            with open(backup_file, "w") as f:
                subprocess.run(cmd, cwd=self.root_dir, stdout=f, check=True)
            
            print_success("Database backup completed")
        except subprocess.CalledProcessError:
            print_error("Database backup failed")
    
    def _backup_files(self, backup_dir: Path):
        """Backup important files."""
        import shutil
        
        files_to_backup = [
            "backend/.env",
            "frontend/.env.local",
            "docker-compose.yaml",
            "logs"
        ]
        
        for file_path in files_to_backup:
            source = self.root_dir / file_path
            if source.exists():
                if source.is_file():
                    shutil.copy2(source, backup_dir)
                else:
                    shutil.copytree(source, backup_dir / source.name)
        
        print_success("Files backup completed")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Enhanced NEO Service Manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start NEO services")
    start_parser.add_argument("--dev", action="store_true", help="Start in development mode")
    start_parser.add_argument("--logs", action="store_true", help="Show logs after starting")
    start_parser.add_argument("--profile", help="Use specific configuration profile")
    
    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop NEO services")
    stop_parser.add_argument("--force", action="store_true", help="Force stop all services")
    
    # Restart command
    restart_parser = subparsers.add_parser("restart", help="Restart NEO services")
    restart_parser.add_argument("--service", help="Restart specific service")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show service status")
    status_parser.add_argument("--detailed", action="store_true", help="Show detailed status")
    
    # Logs command
    logs_parser = subparsers.add_parser("logs", help="Show service logs")
    logs_parser.add_argument("--follow", "-f", action="store_true", help="Follow log output")
    logs_parser.add_argument("--service", help="Show logs for specific service")
    logs_parser.add_argument("--lines", type=int, default=100, help="Number of lines to show")
    
    # Health command
    health_parser = subparsers.add_parser("health", help="Perform health check")
    health_parser.add_argument("--fix", action="store_true", help="Attempt to fix issues")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Setup NEO environment")
    setup_parser.add_argument("--reset", action="store_true", help="Reset configuration")
    
    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Monitor services")
    monitor_parser.add_argument("--interval", type=int, default=30, help="Monitor interval in seconds")
    
    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Backup NEO data")
    backup_parser.add_argument("--type", choices=["full", "database", "files"], default="full")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = NEOManager()
    
    try:
        if args.command == "start":
            if not manager.check_prerequisites():
                print_error("Prerequisites not met. Run 'python neo_manager.py setup' first.")
                return
            
            success = True
            success &= manager.start_docker_services()
            success &= manager.start_process_services(dev_mode=args.dev)
            
            if success:
                print_success("NEO started successfully!")
                manager.print_status()
                
                if args.logs:
                    print_info("Starting log monitoring...")
                    manager.monitor_services()
            else:
                print_error("Failed to start NEO completely")
        
        elif args.command == "stop":
            manager.stop_services(force=args.force)
        
        elif args.command == "restart":
            if args.service:
                print_info(f"Restarting {args.service}...")
                # Implement single service restart
            else:
                manager.stop_services()
                time.sleep(2)
                manager.start_docker_services()
                manager.start_process_services()
        
        elif args.command == "status":
            manager.print_status(detailed=args.detailed)
        
        elif args.command == "health":
            manager.health_check(fix_issues=args.fix)
        
        elif args.command == "setup":
            manager.setup_environment(reset=args.reset)
        
        elif args.command == "monitor":
            manager.monitor_services(interval=args.interval)
        
        elif args.command == "backup":
            manager.backup_data(backup_type=args.type)
        
        elif args.command == "logs":
            # Implement log viewing
            if args.service:
                print_info(f"Showing logs for {args.service}")
            else:
                print_info("Showing logs for all services")
    
    except KeyboardInterrupt:
        print_info("Operation cancelled by user")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()