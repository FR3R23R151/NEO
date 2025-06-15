#!/usr/bin/env python3
"""
NEO Startup Script

Manages the startup and shutdown of the NEO system with all local services.
Replaces the original start.py with support for the new architecture.
"""

import os
import sys
import subprocess
import time
import signal
import argparse
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """Run a shell command."""
    print(f"Running: {command}")
    if cwd:
        print(f"Working directory: {cwd}")
    
    result = subprocess.run(
        command,
        shell=True,
        cwd=cwd,
        capture_output=False,
        check=check
    )
    return result.returncode == 0

def check_docker():
    """Check if Docker is running."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_docker_compose():
    """Check if Docker Compose is available."""
    try:
        result = subprocess.run(
            ["docker-compose", "--version"],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            result = subprocess.run(
                ["docker", "compose", "version"],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

def get_compose_command():
    """Get the appropriate Docker Compose command."""
    try:
        subprocess.run(
            ["docker-compose", "--version"],
            capture_output=True,
            check=True
        )
        return "docker-compose"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "docker compose"

def check_env_file():
    """Check if .env file exists and create from example if not."""
    env_file = Path("backend/.env")
    env_example = Path("backend/.env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("Creating .env file from .env.example...")
            import shutil
            shutil.copy(env_example, env_file)
            print("⚠️  Please edit backend/.env with your configuration before starting NEO")
            return False
        else:
            print("❌ No .env.example file found!")
            return False
    return True

def start_services(detached=True):
    """Start all NEO services."""
    print("🚀 Starting NEO services...")
    
    compose_cmd = get_compose_command()
    
    # Build and start services
    if detached:
        success = run_command(f"{compose_cmd} up -d --build")
    else:
        success = run_command(f"{compose_cmd} up --build")
    
    if success:
        print("✅ NEO services started successfully!")
        print("\n📊 Service Status:")
        run_command(f"{compose_cmd} ps")
        
        print("\n🌐 Access URLs:")
        print("  Frontend: http://localhost:3000")
        print("  Backend API: http://localhost:8000")
        print("  Isolator Service: http://localhost:8001")
        print("  MinIO Console: http://localhost:9001")
        print("  RabbitMQ Management: http://localhost:15672")
        
        print("\n📝 Default Credentials:")
        print("  MinIO: neo_minio / neo_minio_password")
        print("  RabbitMQ: neo_rabbit / neo_rabbit_password")
        print("  Database: neo_user / neo_password")
        
        return True
    else:
        print("❌ Failed to start NEO services!")
        return False

def stop_services():
    """Stop all NEO services."""
    print("🛑 Stopping NEO services...")
    
    compose_cmd = get_compose_command()
    success = run_command(f"{compose_cmd} down")
    
    if success:
        print("✅ NEO services stopped successfully!")
        return True
    else:
        print("❌ Failed to stop NEO services!")
        return False

def restart_services():
    """Restart all NEO services."""
    print("🔄 Restarting NEO services...")
    stop_services()
    time.sleep(2)
    return start_services()

def show_logs(service=None, follow=False):
    """Show logs for services."""
    compose_cmd = get_compose_command()
    
    if service:
        cmd = f"{compose_cmd} logs"
        if follow:
            cmd += " -f"
        cmd += f" {service}"
    else:
        cmd = f"{compose_cmd} logs"
        if follow:
            cmd += " -f"
    
    run_command(cmd, check=False)

def show_status():
    """Show status of all services."""
    compose_cmd = get_compose_command()
    
    print("📊 NEO Service Status:")
    run_command(f"{compose_cmd} ps")
    
    print("\n💾 Volume Usage:")
    run_command("docker volume ls | grep neo")
    
    print("\n🌐 Network Status:")
    run_command("docker network ls | grep neo")

def cleanup():
    """Clean up all NEO resources."""
    print("🧹 Cleaning up NEO resources...")
    
    compose_cmd = get_compose_command()
    
    # Stop and remove containers
    run_command(f"{compose_cmd} down -v --remove-orphans", check=False)
    
    # Remove images
    print("Removing NEO images...")
    run_command("docker images | grep neo | awk '{print $3}' | xargs -r docker rmi", check=False)
    
    # Remove volumes
    print("Removing NEO volumes...")
    run_command("docker volume ls | grep neo | awk '{print $2}' | xargs -r docker volume rm", check=False)
    
    print("✅ Cleanup completed!")

def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown."""
    def signal_handler(sig, frame):
        print("\n🛑 Received interrupt signal, stopping services...")
        stop_services()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="NEO Service Manager")
    parser.add_argument(
        "action",
        choices=["start", "stop", "restart", "status", "logs", "cleanup"],
        help="Action to perform"
    )
    parser.add_argument(
        "--service",
        help="Specific service for logs command"
    )
    parser.add_argument(
        "--follow", "-f",
        action="store_true",
        help="Follow logs output"
    )
    parser.add_argument(
        "--foreground",
        action="store_true",
        help="Run services in foreground (not detached)"
    )
    
    args = parser.parse_args()
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("🤖 NEO Service Manager")
    print("=" * 50)
    
    # Check prerequisites
    if not check_docker():
        print("❌ Docker is not running or not installed!")
        print("Please install and start Docker first.")
        sys.exit(1)
    
    if not check_docker_compose():
        print("❌ Docker Compose is not available!")
        print("Please install Docker Compose first.")
        sys.exit(1)
    
    # Handle actions
    if args.action == "start":
        if not check_env_file():
            sys.exit(1)
        
        setup_signal_handlers()
        success = start_services(detached=not args.foreground)
        
        if success and args.foreground:
            print("\n📝 Press Ctrl+C to stop services...")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                stop_services()
        
        sys.exit(0 if success else 1)
    
    elif args.action == "stop":
        success = stop_services()
        sys.exit(0 if success else 1)
    
    elif args.action == "restart":
        success = restart_services()
        sys.exit(0 if success else 1)
    
    elif args.action == "status":
        show_status()
    
    elif args.action == "logs":
        show_logs(args.service, args.follow)
    
    elif args.action == "cleanup":
        confirm = input("⚠️  This will remove all NEO data! Continue? (y/N): ")
        if confirm.lower() == 'y':
            cleanup()
        else:
            print("Cleanup cancelled.")

if __name__ == "__main__":
    main()