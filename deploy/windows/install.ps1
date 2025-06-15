# NEO Windows Installation Script
# This script installs NEO on Windows with all dependencies

param(
    [string]$InstallPath = "$env:USERPROFILE\NEO",
    [switch]$SkipDocker = $false,
    [switch]$DevMode = $false,
    [switch]$Verbose = $false
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Enable verbose output if requested
if ($Verbose) {
    $VerbosePreference = "Continue"
}

Write-Host "🚀 NEO Windows Installer" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

# Function to check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Function to install Chocolatey
function Install-Chocolatey {
    Write-Host "📦 Installing Chocolatey package manager..." -ForegroundColor Yellow
    
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        Write-Host "✅ Chocolatey already installed" -ForegroundColor Green
        return
    }
    
    try {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        
        # Refresh environment variables
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        Write-Host "✅ Chocolatey installed successfully" -ForegroundColor Green
    }
    catch {
        Write-Error "❌ Failed to install Chocolatey: $_"
        exit 1
    }
}

# Function to install Git
function Install-Git {
    Write-Host "📦 Installing Git..." -ForegroundColor Yellow
    
    if (Get-Command git -ErrorAction SilentlyContinue) {
        Write-Host "✅ Git already installed" -ForegroundColor Green
        return
    }
    
    try {
        choco install git -y
        # Refresh environment variables
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        Write-Host "✅ Git installed successfully" -ForegroundColor Green
    }
    catch {
        Write-Error "❌ Failed to install Git: $_"
        exit 1
    }
}

# Function to install Docker Desktop
function Install-Docker {
    if ($SkipDocker) {
        Write-Host "⏭️ Skipping Docker installation" -ForegroundColor Yellow
        return
    }
    
    Write-Host "🐳 Installing Docker Desktop..." -ForegroundColor Yellow
    
    if (Get-Command docker -ErrorAction SilentlyContinue) {
        Write-Host "✅ Docker already installed" -ForegroundColor Green
        return
    }
    
    try {
        choco install docker-desktop -y
        Write-Host "✅ Docker Desktop installed successfully" -ForegroundColor Green
        Write-Host "⚠️ Please restart your computer and start Docker Desktop before continuing" -ForegroundColor Yellow
        
        $restart = Read-Host "Do you want to restart now? (y/N)"
        if ($restart -eq "y" -or $restart -eq "Y") {
            Restart-Computer -Force
        }
    }
    catch {
        Write-Error "❌ Failed to install Docker Desktop: $_"
        Write-Host "💡 You can install Docker Desktop manually from: https://www.docker.com/products/docker-desktop" -ForegroundColor Cyan
    }
}

# Function to install Python
function Install-Python {
    Write-Host "🐍 Installing Python..." -ForegroundColor Yellow
    
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python 3\.[8-9]|Python 3\.1[0-9]") {
            Write-Host "✅ Python already installed: $pythonVersion" -ForegroundColor Green
            return
        }
    }
    
    try {
        choco install python -y
        # Refresh environment variables
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        Write-Host "✅ Python installed successfully" -ForegroundColor Green
    }
    catch {
        Write-Error "❌ Failed to install Python: $_"
        exit 1
    }
}

# Function to install Node.js
function Install-NodeJS {
    Write-Host "📦 Installing Node.js..." -ForegroundColor Yellow
    
    if (Get-Command node -ErrorAction SilentlyContinue) {
        $nodeVersion = node --version 2>&1
        if ($nodeVersion -match "v1[8-9]\.|v[2-9][0-9]\.") {
            Write-Host "✅ Node.js already installed: $nodeVersion" -ForegroundColor Green
            return
        }
    }
    
    try {
        choco install nodejs -y
        # Refresh environment variables
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        Write-Host "✅ Node.js installed successfully" -ForegroundColor Green
    }
    catch {
        Write-Error "❌ Failed to install Node.js: $_"
        exit 1
    }
}

# Function to clone NEO repository
function Clone-NEORepository {
    Write-Host "📥 Cloning NEO repository..." -ForegroundColor Yellow
    
    if (Test-Path $InstallPath) {
        Write-Host "⚠️ Installation directory already exists: $InstallPath" -ForegroundColor Yellow
        $overwrite = Read-Host "Do you want to overwrite it? (y/N)"
        if ($overwrite -eq "y" -or $overwrite -eq "Y") {
            Remove-Item -Path $InstallPath -Recurse -Force
        } else {
            Write-Host "❌ Installation cancelled" -ForegroundColor Red
            exit 1
        }
    }
    
    try {
        git clone https://github.com/kortix-ai/suna.git $InstallPath
        Write-Host "✅ NEO repository cloned successfully" -ForegroundColor Green
    }
    catch {
        Write-Error "❌ Failed to clone NEO repository: $_"
        exit 1
    }
}

# Function to setup Python environment
function Setup-PythonEnvironment {
    Write-Host "🐍 Setting up Python environment..." -ForegroundColor Yellow
    
    Set-Location "$InstallPath\backend"
    
    try {
        # Install Poetry
        if (-not (Get-Command poetry -ErrorAction SilentlyContinue)) {
            Write-Host "📦 Installing Poetry..." -ForegroundColor Yellow
            (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
            
            # Add Poetry to PATH
            $poetryPath = "$env:APPDATA\Python\Scripts"
            if ($env:Path -notlike "*$poetryPath*") {
                [Environment]::SetEnvironmentVariable("Path", $env:Path + ";$poetryPath", "User")
                $env:Path += ";$poetryPath"
            }
        }
        
        # Install dependencies
        Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
        poetry install
        
        Write-Host "✅ Python environment setup completed" -ForegroundColor Green
    }
    catch {
        Write-Error "❌ Failed to setup Python environment: $_"
        exit 1
    }
}

# Function to setup Node.js environment
function Setup-NodeEnvironment {
    Write-Host "📦 Setting up Node.js environment..." -ForegroundColor Yellow
    
    Set-Location "$InstallPath\frontend"
    
    try {
        npm install
        Write-Host "✅ Node.js environment setup completed" -ForegroundColor Green
    }
    catch {
        Write-Error "❌ Failed to setup Node.js environment: $_"
        exit 1
    }
}

# Function to create environment files
function Create-EnvironmentFiles {
    Write-Host "⚙️ Creating environment configuration..." -ForegroundColor Yellow
    
    try {
        # Backend .env file
        $backendEnvPath = "$InstallPath\backend\.env"
        if (-not (Test-Path $backendEnvPath)) {
            Copy-Item "$InstallPath\backend\.env.example" $backendEnvPath
            Write-Host "✅ Backend .env file created" -ForegroundColor Green
        }
        
        # Frontend .env file
        $frontendEnvPath = "$InstallPath\frontend\.env.local"
        if (-not (Test-Path $frontendEnvPath)) {
            @"
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ISOLATOR_URL=http://localhost:8001
NEXT_PUBLIC_MINIO_URL=http://localhost:9000
"@ | Out-File -FilePath $frontendEnvPath -Encoding UTF8
            Write-Host "✅ Frontend .env file created" -ForegroundColor Green
        }
        
        Write-Host "✅ Environment files created" -ForegroundColor Green
    }
    catch {
        Write-Error "❌ Failed to create environment files: $_"
        exit 1
    }
}

# Function to create Windows service scripts
function Create-ServiceScripts {
    Write-Host "🔧 Creating Windows service scripts..." -ForegroundColor Yellow
    
    $scriptsPath = "$InstallPath\scripts\windows"
    New-Item -ItemType Directory -Path $scriptsPath -Force | Out-Null
    
    # Start script
    $startScript = @"
@echo off
echo Starting NEO services...
cd /d "$InstallPath"

echo Starting Docker services...
docker-compose up -d postgres redis minio rabbitmq

echo Waiting for services to be ready...
timeout /t 10

echo Starting NEO Isolator...
start "NEO Isolator" cmd /k "cd backend && poetry run python -m isolator.main"

echo Starting NEO Backend...
start "NEO Backend" cmd /k "cd backend && poetry run python api_new.py"

echo Starting NEO Frontend...
start "NEO Frontend" cmd /k "cd frontend && npm run dev"

echo NEO services started successfully!
echo.
echo Access NEO at: http://localhost:3000
echo Backend API: http://localhost:8000
echo Isolator: http://localhost:8001
echo MinIO Console: http://localhost:9001
echo.
pause
"@
    
    $startScript | Out-File -FilePath "$scriptsPath\start.bat" -Encoding ASCII
    
    # Stop script
    $stopScript = @"
@echo off
echo Stopping NEO services...
cd /d "$InstallPath"

echo Stopping Docker services...
docker-compose down

echo Stopping Node.js processes...
taskkill /f /im node.exe 2>nul

echo Stopping Python processes...
taskkill /f /im python.exe 2>nul

echo NEO services stopped.
pause
"@
    
    $stopScript | Out-File -FilePath "$scriptsPath\stop.bat" -Encoding ASCII
    
    # Status script
    $statusScript = @"
@echo off
echo NEO Service Status
echo ==================
echo.

echo Docker containers:
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo Node.js processes:
tasklist /fi "imagename eq node.exe" /fo table 2>nul

echo.
echo Python processes:
tasklist /fi "imagename eq python.exe" /fo table 2>nul

pause
"@
    
    $statusScript | Out-File -FilePath "$scriptsPath\status.bat" -Encoding ASCII
    
    Write-Host "✅ Windows service scripts created" -ForegroundColor Green
}

# Function to create desktop shortcuts
function Create-DesktopShortcuts {
    Write-Host "🔗 Creating desktop shortcuts..." -ForegroundColor Yellow
    
    try {
        $WshShell = New-Object -comObject WScript.Shell
        
        # Start NEO shortcut
        $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Start NEO.lnk")
        $Shortcut.TargetPath = "$InstallPath\scripts\windows\start.bat"
        $Shortcut.WorkingDirectory = $InstallPath
        $Shortcut.IconLocation = "$InstallPath\frontend\public\favicon.ico"
        $Shortcut.Description = "Start NEO AI Agent Platform"
        $Shortcut.Save()
        
        # Stop NEO shortcut
        $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Stop NEO.lnk")
        $Shortcut.TargetPath = "$InstallPath\scripts\windows\stop.bat"
        $Shortcut.WorkingDirectory = $InstallPath
        $Shortcut.Description = "Stop NEO AI Agent Platform"
        $Shortcut.Save()
        
        Write-Host "✅ Desktop shortcuts created" -ForegroundColor Green
    }
    catch {
        Write-Warning "⚠️ Failed to create desktop shortcuts: $_"
    }
}

# Function to test installation
function Test-Installation {
    Write-Host "🧪 Testing installation..." -ForegroundColor Yellow
    
    Set-Location $InstallPath
    
    try {
        # Test Docker
        if (-not $SkipDocker) {
            Write-Host "Testing Docker..." -ForegroundColor Cyan
            $dockerVersion = docker --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Docker: $dockerVersion" -ForegroundColor Green
            } else {
                Write-Warning "⚠️ Docker not working properly"
            }
        }
        
        # Test Python
        Write-Host "Testing Python environment..." -ForegroundColor Cyan
        Set-Location "$InstallPath\backend"
        $poetryCheck = poetry check 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Python environment: OK" -ForegroundColor Green
        } else {
            Write-Warning "⚠️ Python environment issues detected"
        }
        
        # Test Node.js
        Write-Host "Testing Node.js environment..." -ForegroundColor Cyan
        Set-Location "$InstallPath\frontend"
        if (Test-Path "node_modules") {
            Write-Host "✅ Node.js environment: OK" -ForegroundColor Green
        } else {
            Write-Warning "⚠️ Node.js dependencies not installed properly"
        }
        
        Write-Host "✅ Installation test completed" -ForegroundColor Green
    }
    catch {
        Write-Warning "⚠️ Some tests failed: $_"
    }
}

# Function to display final instructions
function Show-FinalInstructions {
    Write-Host ""
    Write-Host "🎉 NEO Installation Completed!" -ForegroundColor Green
    Write-Host "===============================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Installation Location: $InstallPath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To start NEO:" -ForegroundColor Yellow
    Write-Host "1. Double-click 'Start NEO' on your desktop, OR" -ForegroundColor White
    Write-Host "2. Run: $InstallPath\scripts\windows\start.bat" -ForegroundColor White
    Write-Host ""
    Write-Host "To stop NEO:" -ForegroundColor Yellow
    Write-Host "1. Double-click 'Stop NEO' on your desktop, OR" -ForegroundColor White
    Write-Host "2. Run: $InstallPath\scripts\windows\stop.bat" -ForegroundColor White
    Write-Host ""
    Write-Host "Access URLs:" -ForegroundColor Yellow
    Write-Host "• NEO Web Interface: http://localhost:3000" -ForegroundColor White
    Write-Host "• Backend API: http://localhost:8000" -ForegroundColor White
    Write-Host "• Isolator Service: http://localhost:8001" -ForegroundColor White
    Write-Host "• MinIO Console: http://localhost:9001" -ForegroundColor White
    Write-Host ""
    Write-Host "Configuration Files:" -ForegroundColor Yellow
    Write-Host "• Backend: $InstallPath\backend\.env" -ForegroundColor White
    Write-Host "• Frontend: $InstallPath\frontend\.env.local" -ForegroundColor White
    Write-Host ""
    Write-Host "Documentation:" -ForegroundColor Yellow
    Write-Host "• Architecture: $InstallPath\docs\ARCHITECTURE.md" -ForegroundColor White
    Write-Host "• Migration Report: $InstallPath\MIGRATION_REPORT.md" -ForegroundColor White
    Write-Host "• UI/UX Guide: $InstallPath\UI_UX_REDESIGN_REPORT.md" -ForegroundColor White
    Write-Host ""
    
    if (-not $SkipDocker) {
        Write-Host "⚠️ Important Notes:" -ForegroundColor Red
        Write-Host "• Make sure Docker Desktop is running before starting NEO" -ForegroundColor White
        Write-Host "• First startup may take a few minutes to download Docker images" -ForegroundColor White
        Write-Host ""
    }
    
    Write-Host "Need help? Check the documentation or visit: https://github.com/kortix-ai/suna" -ForegroundColor Cyan
    Write-Host ""
}

# Main installation process
function Main {
    Write-Host "Starting NEO installation..." -ForegroundColor Green
    Write-Host "Installation path: $InstallPath" -ForegroundColor Cyan
    
    if ($DevMode) {
        Write-Host "🔧 Development mode enabled" -ForegroundColor Yellow
    }
    
    # Check if running as administrator for some operations
    if (-not (Test-Administrator)) {
        Write-Host "⚠️ Not running as administrator. Some features may require elevation." -ForegroundColor Yellow
    }
    
    try {
        # Install prerequisites
        Install-Chocolatey
        Install-Git
        Install-Python
        Install-NodeJS
        Install-Docker
        
        # Clone and setup NEO
        Clone-NEORepository
        Setup-PythonEnvironment
        Setup-NodeEnvironment
        Create-EnvironmentFiles
        
        # Create Windows-specific files
        Create-ServiceScripts
        Create-DesktopShortcuts
        
        # Test installation
        Test-Installation
        
        # Show final instructions
        Show-FinalInstructions
        
        Write-Host "🎉 Installation completed successfully!" -ForegroundColor Green
        
    }
    catch {
        Write-Error "❌ Installation failed: $_"
        Write-Host "Please check the error message above and try again." -ForegroundColor Red
        Write-Host "For help, visit: https://github.com/kortix-ai/suna/issues" -ForegroundColor Cyan
        exit 1
    }
}

# Run main installation
Main