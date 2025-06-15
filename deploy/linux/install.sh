#!/bin/bash

# NEO Linux/macOS Installation Script
# This script installs NEO on Linux and macOS with all dependencies

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
INSTALL_PATH="${HOME}/NEO"
SKIP_DOCKER=false
DEV_MODE=false
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --install-path)
            INSTALL_PATH="$2"
            shift 2
            ;;
        --skip-docker)
            SKIP_DOCKER=true
            shift
            ;;
        --dev)
            DEV_MODE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            echo "NEO Installation Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --install-path PATH    Installation directory (default: ~/NEO)"
            echo "  --skip-docker         Skip Docker installation"
            echo "  --dev                 Enable development mode"
            echo "  --verbose             Enable verbose output"
            echo "  -h, --help            Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Utility functions
print_header() {
    echo -e "${CYAN}============================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}============================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if running on supported OS
check_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if command -v apt-get &> /dev/null; then
            PACKAGE_MANAGER="apt"
        elif command -v yum &> /dev/null; then
            PACKAGE_MANAGER="yum"
        elif command -v dnf &> /dev/null; then
            PACKAGE_MANAGER="dnf"
        elif command -v pacman &> /dev/null; then
            PACKAGE_MANAGER="pacman"
        else
            print_error "Unsupported Linux distribution"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        PACKAGE_MANAGER="brew"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    
    print_success "Detected OS: $OS with package manager: $PACKAGE_MANAGER"
}

# Install package manager if needed (macOS)
install_package_manager() {
    if [[ "$OS" == "macos" ]] && ! command -v brew &> /dev/null; then
        print_info "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH
        if [[ -f "/opt/homebrew/bin/brew" ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        elif [[ -f "/usr/local/bin/brew" ]]; then
            eval "$(/usr/local/bin/brew shellenv)"
        fi
        
        print_success "Homebrew installed"
    fi
}

# Install a package using the appropriate package manager
install_package() {
    local package_name="$1"
    local package_name_alt="$2"  # Alternative package name for different distros
    
    case $PACKAGE_MANAGER in
        apt)
            sudo apt-get update -qq
            sudo apt-get install -y "${package_name_alt:-$package_name}"
            ;;
        yum)
            sudo yum install -y "${package_name_alt:-$package_name}"
            ;;
        dnf)
            sudo dnf install -y "${package_name_alt:-$package_name}"
            ;;
        pacman)
            sudo pacman -S --noconfirm "${package_name_alt:-$package_name}"
            ;;
        brew)
            brew install "$package_name"
            ;;
        *)
            print_error "Unsupported package manager: $PACKAGE_MANAGER"
            return 1
            ;;
    esac
}

# Check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Install Git
install_git() {
    print_info "Installing Git..."
    
    if command_exists git; then
        print_success "Git already installed: $(git --version)"
        return
    fi
    
    install_package "git"
    print_success "Git installed successfully"
}

# Install Python
install_python() {
    print_info "Installing Python..."
    
    if command_exists python3; then
        python_version=$(python3 --version 2>&1)
        if [[ $python_version =~ Python\ 3\.[8-9]|Python\ 3\.1[0-9] ]]; then
            print_success "Python already installed: $python_version"
            return
        fi
    fi
    
    case $PACKAGE_MANAGER in
        apt)
            install_package "python3" "python3"
            install_package "python3-pip" "python3-pip"
            install_package "python3-venv" "python3-venv"
            ;;
        yum|dnf)
            install_package "python3" "python3"
            install_package "python3-pip" "python3-pip"
            ;;
        pacman)
            install_package "python" "python"
            install_package "python-pip" "python-pip"
            ;;
        brew)
            install_package "python@3.11"
            ;;
    esac
    
    print_success "Python installed successfully"
}

# Install Node.js
install_nodejs() {
    print_info "Installing Node.js..."
    
    if command_exists node; then
        node_version=$(node --version 2>&1)
        if [[ $node_version =~ v1[8-9]\.|v[2-9][0-9]\. ]]; then
            print_success "Node.js already installed: $node_version"
            return
        fi
    fi
    
    case $PACKAGE_MANAGER in
        apt)
            # Install NodeSource repository
            curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
            install_package "nodejs"
            ;;
        yum|dnf)
            # Install NodeSource repository
            curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash -
            install_package "nodejs"
            ;;
        pacman)
            install_package "nodejs"
            install_package "npm"
            ;;
        brew)
            install_package "node"
            ;;
    esac
    
    print_success "Node.js installed successfully"
}

# Install Docker
install_docker() {
    if [[ "$SKIP_DOCKER" == "true" ]]; then
        print_warning "Skipping Docker installation"
        return
    fi
    
    print_info "Installing Docker..."
    
    if command_exists docker; then
        print_success "Docker already installed: $(docker --version)"
        return
    fi
    
    case $OS in
        linux)
            # Install Docker using official script
            curl -fsSL https://get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
            rm get-docker.sh
            
            # Add user to docker group
            sudo usermod -aG docker "$USER"
            
            # Install Docker Compose
            if ! command_exists docker-compose; then
                sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                sudo chmod +x /usr/local/bin/docker-compose
            fi
            
            # Start Docker service
            sudo systemctl enable docker
            sudo systemctl start docker
            ;;
        macos)
            print_info "Please install Docker Desktop for Mac manually from:"
            print_info "https://www.docker.com/products/docker-desktop"
            print_warning "Docker Desktop installation requires manual intervention"
            ;;
    esac
    
    print_success "Docker installation completed"
}

# Install Poetry
install_poetry() {
    print_info "Installing Poetry..."
    
    if command_exists poetry; then
        print_success "Poetry already installed: $(poetry --version)"
        return
    fi
    
    # Install Poetry using official installer
    curl -sSL https://install.python-poetry.org | python3 -
    
    # Add Poetry to PATH
    export PATH="$HOME/.local/bin:$PATH"
    
    # Add to shell profile
    if [[ -f "$HOME/.bashrc" ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    fi
    
    if [[ -f "$HOME/.zshrc" ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
    fi
    
    print_success "Poetry installed successfully"
}

# Clone NEO repository
clone_repository() {
    print_info "Cloning NEO repository..."
    
    if [[ -d "$INSTALL_PATH" ]]; then
        print_warning "Installation directory already exists: $INSTALL_PATH"
        read -p "Do you want to overwrite it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$INSTALL_PATH"
        else
            print_error "Installation cancelled"
            exit 1
        fi
    fi
    
    git clone https://github.com/kortix-ai/suna.git "$INSTALL_PATH"
    print_success "NEO repository cloned successfully"
}

# Setup Python environment
setup_python_environment() {
    print_info "Setting up Python environment..."
    
    cd "$INSTALL_PATH/backend"
    
    # Install dependencies using Poetry
    poetry install
    
    print_success "Python environment setup completed"
}

# Setup Node.js environment
setup_nodejs_environment() {
    print_info "Setting up Node.js environment..."
    
    cd "$INSTALL_PATH/frontend"
    
    # Install dependencies
    npm install
    
    print_success "Node.js environment setup completed"
}

# Create environment files
create_environment_files() {
    print_info "Creating environment configuration..."
    
    # Backend .env file
    if [[ ! -f "$INSTALL_PATH/backend/.env" ]]; then
        cp "$INSTALL_PATH/backend/.env.example" "$INSTALL_PATH/backend/.env"
        print_success "Backend .env file created"
    fi
    
    # Frontend .env file
    if [[ ! -f "$INSTALL_PATH/frontend/.env.local" ]]; then
        cat > "$INSTALL_PATH/frontend/.env.local" << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ISOLATOR_URL=http://localhost:8001
NEXT_PUBLIC_MINIO_URL=http://localhost:9000
EOF
        print_success "Frontend .env file created"
    fi
}

# Create service scripts
create_service_scripts() {
    print_info "Creating service scripts..."
    
    mkdir -p "$INSTALL_PATH/scripts/unix"
    
    # Start script
    cat > "$INSTALL_PATH/scripts/unix/start.sh" << 'EOF'
#!/bin/bash

echo "Starting NEO services..."
cd "$(dirname "$0")/../.."

echo "Starting Docker services..."
docker-compose up -d postgres redis minio rabbitmq

echo "Waiting for services to be ready..."
sleep 10

echo "Starting NEO Isolator..."
cd backend
poetry run python -m isolator.main &
ISOLATOR_PID=$!

echo "Starting NEO Backend..."
poetry run python api_new.py &
BACKEND_PID=$!

cd ../frontend
echo "Starting NEO Frontend..."
npm run dev &
FRONTEND_PID=$!

echo "NEO services started successfully!"
echo ""
echo "Access NEO at: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "Isolator: http://localhost:8001"
echo "MinIO Console: http://localhost:9001"
echo ""
echo "Process IDs:"
echo "Isolator: $ISOLATOR_PID"
echo "Backend: $BACKEND_PID"
echo "Frontend: $FRONTEND_PID"
echo ""
echo "To stop services, run: ./scripts/unix/stop.sh"
EOF

    # Stop script
    cat > "$INSTALL_PATH/scripts/unix/stop.sh" << 'EOF'
#!/bin/bash

echo "Stopping NEO services..."
cd "$(dirname "$0")/../.."

echo "Stopping Docker services..."
docker-compose down

echo "Stopping Node.js processes..."
pkill -f "npm run dev" || true
pkill -f "next dev" || true

echo "Stopping Python processes..."
pkill -f "python.*api_new.py" || true
pkill -f "python.*isolator.main" || true

echo "NEO services stopped."
EOF

    # Status script
    cat > "$INSTALL_PATH/scripts/unix/status.sh" << 'EOF'
#!/bin/bash

echo "NEO Service Status"
echo "=================="
echo ""

echo "Docker containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "Node.js processes:"
pgrep -f "npm run dev" > /dev/null && echo "Frontend: Running" || echo "Frontend: Stopped"

echo ""
echo "Python processes:"
pgrep -f "python.*api_new.py" > /dev/null && echo "Backend: Running" || echo "Backend: Stopped"
pgrep -f "python.*isolator.main" > /dev/null && echo "Isolator: Running" || echo "Isolator: Stopped"
EOF

    # Make scripts executable
    chmod +x "$INSTALL_PATH/scripts/unix/"*.sh
    
    print_success "Service scripts created"
}

# Create desktop shortcuts (Linux only)
create_desktop_shortcuts() {
    if [[ "$OS" != "linux" ]]; then
        return
    fi
    
    print_info "Creating desktop shortcuts..."
    
    # Create desktop directory if it doesn't exist
    mkdir -p "$HOME/Desktop"
    
    # Start NEO shortcut
    cat > "$HOME/Desktop/Start NEO.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Start NEO
Comment=Start NEO AI Agent Platform
Exec=$INSTALL_PATH/scripts/unix/start.sh
Icon=$INSTALL_PATH/frontend/public/favicon.ico
Terminal=true
Categories=Development;
EOF

    # Stop NEO shortcut
    cat > "$HOME/Desktop/Stop NEO.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Stop NEO
Comment=Stop NEO AI Agent Platform
Exec=$INSTALL_PATH/scripts/unix/stop.sh
Icon=$INSTALL_PATH/frontend/public/favicon.ico
Terminal=true
Categories=Development;
EOF

    # Make desktop files executable
    chmod +x "$HOME/Desktop/Start NEO.desktop"
    chmod +x "$HOME/Desktop/Stop NEO.desktop"
    
    print_success "Desktop shortcuts created"
}

# Test installation
test_installation() {
    print_info "Testing installation..."
    
    cd "$INSTALL_PATH"
    
    # Test Docker
    if [[ "$SKIP_DOCKER" != "true" ]]; then
        if docker --version &> /dev/null; then
            print_success "Docker: $(docker --version)"
        else
            print_warning "Docker not working properly"
        fi
    fi
    
    # Test Python environment
    cd "$INSTALL_PATH/backend"
    if poetry check &> /dev/null; then
        print_success "Python environment: OK"
    else
        print_warning "Python environment issues detected"
    fi
    
    # Test Node.js environment
    cd "$INSTALL_PATH/frontend"
    if [[ -d "node_modules" ]]; then
        print_success "Node.js environment: OK"
    else
        print_warning "Node.js dependencies not installed properly"
    fi
    
    print_success "Installation test completed"
}

# Display final instructions
show_final_instructions() {
    print_header "NEO Installation Completed!"
    echo ""
    print_info "Installation Location: $INSTALL_PATH"
    echo ""
    print_warning "To start NEO:"
    echo "  cd $INSTALL_PATH"
    echo "  ./scripts/unix/start.sh"
    echo ""
    print_warning "To stop NEO:"
    echo "  cd $INSTALL_PATH"
    echo "  ./scripts/unix/stop.sh"
    echo ""
    print_warning "Access URLs:"
    echo "  • NEO Web Interface: http://localhost:3000"
    echo "  • Backend API: http://localhost:8000"
    echo "  • Isolator Service: http://localhost:8001"
    echo "  • MinIO Console: http://localhost:9001"
    echo ""
    print_warning "Configuration Files:"
    echo "  • Backend: $INSTALL_PATH/backend/.env"
    echo "  • Frontend: $INSTALL_PATH/frontend/.env.local"
    echo ""
    print_warning "Documentation:"
    echo "  • Architecture: $INSTALL_PATH/docs/ARCHITECTURE.md"
    echo "  • Migration Report: $INSTALL_PATH/MIGRATION_REPORT.md"
    echo "  • UI/UX Guide: $INSTALL_PATH/UI_UX_REDESIGN_REPORT.md"
    echo ""
    
    if [[ "$SKIP_DOCKER" != "true" ]]; then
        print_error "Important Notes:"
        echo "  • Make sure Docker is running before starting NEO"
        echo "  • First startup may take a few minutes to download Docker images"
        if [[ "$OS" == "linux" ]]; then
            echo "  • You may need to log out and back in for Docker group membership to take effect"
        fi
        echo ""
    fi
    
    print_info "Need help? Check the documentation or visit: https://github.com/kortix-ai/suna"
    echo ""
}

# Main installation function
main() {
    print_header "NEO Linux/macOS Installer"
    
    print_info "Starting NEO installation..."
    print_info "Installation path: $INSTALL_PATH"
    
    if [[ "$DEV_MODE" == "true" ]]; then
        print_warning "Development mode enabled"
    fi
    
    # Check OS and package manager
    check_os
    
    # Install package manager if needed
    install_package_manager
    
    # Install prerequisites
    install_git
    install_python
    install_nodejs
    install_docker
    install_poetry
    
    # Clone and setup NEO
    clone_repository
    setup_python_environment
    setup_nodejs_environment
    create_environment_files
    
    # Create platform-specific files
    create_service_scripts
    create_desktop_shortcuts
    
    # Test installation
    test_installation
    
    # Show final instructions
    show_final_instructions
    
    print_success "Installation completed successfully!"
}

# Run main function
main "$@"