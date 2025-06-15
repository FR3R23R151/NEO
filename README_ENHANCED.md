# NEO - Enhanced AI Agent Platform

<div align="center">

![NEO Logo](frontend/public/favicon.png)

**The Future of AI Automation - Enhanced, Stable, and Autonomous**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)

[🚀 Quick Start](#-quick-start) • [📖 Documentation](#-documentation) • [🛠️ Features](#️-features) • [💻 Installation](#-installation) • [🔧 Configuration](#-configuration)

</div>

## 🌟 What's New in Enhanced NEO

NEO has been completely redesigned with enhanced stability, autonomy, and ease of deployment:

### ✨ **Enhanced Agent Capabilities**
- **🧠 Intelligent Error Recovery**: Automatic error detection, categorization, and recovery
- **🔄 Self-Healing Architecture**: Proactive monitoring and auto-recovery mechanisms  
- **📊 Performance Optimization**: Real-time performance monitoring and adaptive behavior
- **🎯 Context Awareness**: Advanced context management and memory preservation
- **🔒 Circuit Breaker Protection**: Prevents cascading failures in external services

### 🚀 **One-Click Deployment**
- **🪟 Windows**: PowerShell installer with automatic dependency management
- **🐧 Linux**: Bash installer with package manager detection
- **🍎 macOS**: Homebrew-based installation with native integration
- **🐳 Docker**: Fully containerized local stack with no external dependencies

### 📈 **Advanced Monitoring**
- **📊 Real-time Metrics**: CPU, memory, disk, and network monitoring
- **⚡ Performance Analytics**: Response times, throughput, and error rates
- **🚨 Intelligent Alerts**: Threshold-based and anomaly detection alerts
- **🔍 Detailed Diagnostics**: Comprehensive health checks and troubleshooting

### 🛡️ **Enterprise-Grade Reliability**
- **🔄 Automatic Failover**: Service dependency management and recovery
- **💾 Data Protection**: Automated backups and disaster recovery
- **🔐 Security Hardening**: Enhanced authentication and access controls
- **📝 Audit Logging**: Comprehensive logging and compliance features

## 🚀 Quick Start

### Windows (One-Click Install)

```powershell
# Run as Administrator (recommended)
iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/kortix-ai/suna/main/deploy/windows/install.ps1'))
```

Or download and run manually:
```powershell
# Download installer
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/kortix-ai/suna/main/deploy/windows/install.ps1" -OutFile "install.ps1"

# Run installer
.\install.ps1
```

### Linux/macOS (One-Click Install)

```bash
# Automatic installation
curl -sSL https://raw.githubusercontent.com/kortix-ai/suna/main/deploy/linux/install.sh | bash
```

Or download and run manually:
```bash
# Download installer
curl -O https://raw.githubusercontent.com/kortix-ai/suna/main/deploy/linux/install.sh

# Make executable and run
chmod +x install.sh
./install.sh
```

### Manual Installation

If you prefer manual installation or need custom configuration:

```bash
# Clone repository
git clone https://github.com/kortix-ai/suna.git
cd suna

# Use enhanced manager
python neo_manager.py setup
python neo_manager.py start
```

## 🛠️ Features

### 🤖 **AI Agent Capabilities**

- **🧠 Advanced Language Models**: Support for Claude, GPT-4, Gemini, and local models
- **🔧 Tool Integration**: 20+ built-in tools for development, analysis, and automation
- **🌐 Web Browsing**: Intelligent web scraping and research capabilities
- **💻 Code Execution**: Secure sandboxed environment for running code
- **📁 File Management**: Advanced file operations and document processing
- **🔍 Vision Analysis**: Image and document analysis capabilities

### 🏗️ **Architecture**

- **🐳 Containerized Services**: PostgreSQL, Redis, MinIO, RabbitMQ
- **⚡ FastAPI Backend**: High-performance async API with automatic documentation
- **🎨 Modern Frontend**: Next.js with responsive design and real-time updates
- **🔒 NEO Isolator**: Custom container management with security controls
- **📊 Monitoring Stack**: Comprehensive metrics and health monitoring

### 🔧 **Development Tools**

- **🛠️ Enhanced Manager**: Intelligent service orchestration and monitoring
- **📊 Performance Monitor**: Real-time metrics and optimization suggestions
- **🚨 Error Handler**: Advanced error recovery and circuit breaker patterns
- **🔍 Health Checks**: Multi-level health monitoring and auto-recovery
- **📝 Comprehensive Logging**: Structured logging with correlation IDs

## 💻 Installation

### Prerequisites

The installers will automatically install these, but you can install manually:

- **Docker Desktop** (Windows/macOS) or **Docker Engine** (Linux)
- **Python 3.8+** with Poetry
- **Node.js 18+** with npm
- **Git** for version control

### Installation Options

#### Option 1: Automated Installer (Recommended)

**Windows:**
```powershell
# Full installation
.\deploy\windows\install.ps1

# Custom installation path
.\deploy\windows\install.ps1 -InstallPath "C:\NEO"

# Skip Docker (if already installed)
.\deploy\windows\install.ps1 -SkipDocker

# Development mode
.\deploy\windows\install.ps1 -DevMode
```

**Linux/macOS:**
```bash
# Full installation
./deploy/linux/install.sh

# Custom installation path
./deploy/linux/install.sh --install-path ~/MyNEO

# Skip Docker
./deploy/linux/install.sh --skip-docker

# Development mode
./deploy/linux/install.sh --dev
```

#### Option 2: Enhanced Manager

```bash
# Clone repository
git clone https://github.com/kortix-ai/suna.git
cd suna

# Setup environment
python neo_manager.py setup

# Start services
python neo_manager.py start

# Monitor services
python neo_manager.py monitor
```

#### Option 3: Manual Setup

```bash
# Clone and setup
git clone https://github.com/kortix-ai/suna.git
cd suna

# Backend setup
cd backend
poetry install
cp .env.example .env

# Frontend setup
cd ../frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start services
docker-compose up -d
cd backend && poetry run python api_new.py &
cd frontend && npm run dev &
```

## 🔧 Configuration

### Environment Variables

#### Backend Configuration (`backend/.env`)

```bash
# Database
DATABASE_URL=postgresql://neo_user:neo_password@localhost:5432/neo_db

# Redis
REDIS_URL=redis://localhost:6379

# MinIO (Object Storage)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=neo_minio
MINIO_SECRET_KEY=neo_minio_password

# API Keys (add your own)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key

# Security
JWT_SECRET=your_jwt_secret_key
ENCRYPTION_KEY=your_encryption_key

# Performance
MAX_WORKERS=4
TIMEOUT_SECONDS=300
```

#### Frontend Configuration (`frontend/.env.local`)

```bash
# API Endpoints
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ISOLATOR_URL=http://localhost:8001
NEXT_PUBLIC_MINIO_URL=http://localhost:9000

# Features
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_MONITORING=true
```

### Service Configuration

#### Enhanced Manager Configuration

```bash
# Start with custom configuration
python neo_manager.py start --profile production

# Monitor with custom interval
python neo_manager.py monitor --interval 60

# Health check with auto-fix
python neo_manager.py health --fix

# Backup with specific type
python neo_manager.py backup --type database
```

## 🎮 Usage

### Starting NEO

#### Windows
```powershell
# Using desktop shortcuts
# Double-click "Start NEO" on desktop

# Using command line
.\scripts\windows\start.bat

# Using enhanced manager
python neo_manager.py start
```

#### Linux/macOS
```bash
# Using scripts
./scripts/unix/start.sh

# Using enhanced manager
python neo_manager.py start

# Development mode
python neo_manager.py start --dev
```

### Accessing NEO

Once started, access NEO through these URLs:

- **🌐 Web Interface**: http://localhost:3000
- **📚 API Documentation**: http://localhost:8000/docs
- **🔧 Backend API**: http://localhost:8000
- **⚙️ Isolator Service**: http://localhost:8001
- **📦 MinIO Console**: http://localhost:9001 (admin/password123)
- **🐰 RabbitMQ Management**: http://localhost:15672 (guest/guest)

### Managing Services

#### Enhanced Manager Commands

```bash
# Service management
python neo_manager.py start           # Start all services
python neo_manager.py stop            # Stop all services
python neo_manager.py restart         # Restart all services
python neo_manager.py status          # Show service status

# Monitoring and diagnostics
python neo_manager.py monitor         # Real-time monitoring
python neo_manager.py health          # Health check
python neo_manager.py logs            # View logs

# Maintenance
python neo_manager.py backup          # Create backup
python neo_manager.py setup --reset   # Reset configuration
```

#### Service Status

```bash
# Check detailed status
python neo_manager.py status --detailed

# Example output:
# NEO Service Status
# ==================
# All services running (8/8)
#
# 🔴 🐳 postgres:5432 - running
# 🔴 🐳 redis:6379 - running
# 🔴 🐳 minio:9000 - running
# 🔴 🐳 rabbitmq:5672 - running
# 🔴 ⚙️ isolator:8001 - running
# 🔴 ⚙️ backend:8000 - running
# 🟡 ⚙️ worker - running
# 🔴 ⚙️ frontend:3000 - running
```

### Using the Agent

#### Basic Chat Interface

1. Open http://localhost:3000
2. Create an account or sign in
3. Start a new conversation
4. Ask the agent to help with tasks like:
   - Code development and debugging
   - Data analysis and visualization
   - Web research and summarization
   - File processing and management
   - System administration tasks

#### Advanced Features

**Tool Usage:**
```
User: "Analyze the sales data in my CSV file and create a visualization"
Agent: I'll help you analyze your sales data. Please upload your CSV file, and I'll:
1. Load and examine the data structure
2. Perform statistical analysis
3. Create appropriate visualizations
4. Provide insights and recommendations
```

**Code Execution:**
```
User: "Create a Python script to process log files"
Agent: I'll create a log processing script for you:

[Uses code execution tool to write, test, and refine the script]
```

**Web Research:**
```
User: "Research the latest trends in AI development"
Agent: I'll research current AI trends for you:

[Uses web browsing tool to gather information from multiple sources]
```

## 📊 Monitoring and Maintenance

### Real-Time Monitoring

```bash
# Start monitoring dashboard
python neo_manager.py monitor

# Monitor specific service
python neo_manager.py monitor --service backend

# Custom monitoring interval
python neo_manager.py monitor --interval 30
```

### Performance Analytics

```bash
# Get performance summary
python neo_manager.py status --detailed

# View performance trends
python neo_manager.py logs --service backend --lines 1000

# Export metrics
python -c "
from backend.utils.performance_monitor import performance_monitor
print(performance_monitor.export_metrics())
"
```

### Health Checks

```bash
# Basic health check
python neo_manager.py health

# Health check with auto-fix
python neo_manager.py health --fix

# Detailed diagnostics
python neo_manager.py status --detailed
```

### Backup and Recovery

```bash
# Create full backup
python neo_manager.py backup --type full

# Database backup only
python neo_manager.py backup --type database

# Files backup only
python neo_manager.py backup --type files

# Restore from backup
python neo_manager.py restore --file backups/neo_backup_20241215_143022
```

## 🔧 Troubleshooting

### Common Issues

#### Services Won't Start

```bash
# Check prerequisites
python neo_manager.py health

# Check Docker status
docker info

# Check logs
python neo_manager.py logs --follow

# Reset and restart
python neo_manager.py stop
python neo_manager.py setup --reset
python neo_manager.py start
```

#### Performance Issues

```bash
# Check system resources
python neo_manager.py monitor

# View performance metrics
python -c "
from backend.utils.performance_monitor import get_performance_summary
import json
print(json.dumps(get_performance_summary(), indent=2))
"

# Optimize configuration
python neo_manager.py health --fix
```

#### Database Connection Issues

```bash
# Check database status
docker-compose ps postgres

# Reset database
docker-compose down
docker volume rm suna_postgres_data
python neo_manager.py start
```

### Getting Help

1. **Check Logs**: `python neo_manager.py logs --follow`
2. **Health Check**: `python neo_manager.py health --fix`
3. **Documentation**: See `docs/` directory
4. **GitHub Issues**: https://github.com/kortix-ai/suna/issues
5. **Community**: Join our Discord/Slack community

## 📖 Documentation

### Architecture Documentation

- **[Architecture Overview](docs/ARCHITECTURE.md)**: System architecture and design decisions
- **[Migration Report](MIGRATION_REPORT.md)**: Migration from Supabase to local stack
- **[UI/UX Redesign](UI_UX_REDESIGN_REPORT.md)**: Modern interface design system
- **[Agent Enhancement](AGENT_ENHANCEMENT_REPORT.md)**: Enhanced agent capabilities

### API Documentation

- **REST API**: http://localhost:8000/docs (when running)
- **GraphQL**: http://localhost:8000/graphql (when running)
- **WebSocket**: ws://localhost:8000/ws

### Development Guides

- **[Contributing Guide](CONTRIBUTING.md)**: How to contribute to NEO
- **[Development Setup](docs/DEVELOPMENT.md)**: Setting up development environment
- **[Testing Guide](docs/TESTING.md)**: Running tests and quality assurance
- **[Deployment Guide](docs/DEPLOYMENT.md)**: Production deployment instructions

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone repository
git clone https://github.com/kortix-ai/suna.git
cd suna

# Setup development environment
python neo_manager.py setup --dev

# Start in development mode
python neo_manager.py start --dev

# Run tests
cd backend && poetry run pytest
cd frontend && npm test
```

### Code Quality

```bash
# Backend linting and formatting
cd backend
poetry run black .
poetry run isort .
poetry run flake8 .

# Frontend linting and formatting
cd frontend
npm run lint
npm run format
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT models and API
- **Anthropic** for Claude models
- **Google** for Gemini models
- **Docker** for containerization platform
- **FastAPI** for the backend framework
- **Next.js** for the frontend framework
- **PostgreSQL** for the database
- **Redis** for caching and sessions
- **MinIO** for object storage
- **RabbitMQ** for message queuing

## 🔗 Links

- **Website**: https://neo-ai.dev
- **Documentation**: https://docs.neo-ai.dev
- **GitHub**: https://github.com/kortix-ai/suna
- **Discord**: https://discord.gg/neo-ai
- **Twitter**: https://twitter.com/neo_ai_platform

---

<div align="center">

**Built with ❤️ by the NEO Team**

[⭐ Star us on GitHub](https://github.com/kortix-ai/suna) • [🐛 Report Bug](https://github.com/kortix-ai/suna/issues) • [💡 Request Feature](https://github.com/kortix-ai/suna/issues)

</div>