# MCP File Server - Automated Setup Script for Windows
# Save this as: setup-mcp-fileserver.ps1
# Run in PowerShell as Administrator

Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "  MCP FILE SERVER SETUP - Automated Installation" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Node.js is installed
Write-Host "[1/5] Checking Node.js installation..." -ForegroundColor Yellow

if (Get-Command node -ErrorAction SilentlyContinue) {
    $nodeVersion = node --version
    Write-Host "✓ Node.js is installed: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Node.js is NOT installed" -ForegroundColor Red
    Write-Host "Please install Node.js from: https://nodejs.org/" -ForegroundColor Yellow
    Write-Host "Or run: winget install OpenJS.NodeJS" -ForegroundColor Yellow
    exit 1
}

# Check if npm is installed
Write-Host "[2/5] Checking npm installation..." -ForegroundColor Yellow

if (Get-Command npm -ErrorAction SilentlyContinue) {
    $npmVersion = npm --version
    Write-Host "✓ npm is installed: $npmVersion" -ForegroundColor Green
} else {
    Write-Host "✗ npm is NOT installed" -ForegroundColor Red
    exit 1
}

# Install MCP file server
Write-Host "[3/5] Installing MCP file server..." -ForegroundColor Yellow

try {
    npm install -g @modelcontextprotocol/server-filesystem
    Write-Host "✓ MCP file server installed successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to install MCP file server" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}

# Locate Claude Desktop config
Write-Host "[4/5] Locating Claude Desktop configuration..." -ForegroundColor Yellow

$configPath = "$env:APPDATA\Claude\claude_desktop_config.json"
$configDir = "$env:APPDATA\Claude"

if (-not (Test-Path $configDir)) {
    Write-Host "Creating Claude config directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
}

# Create or update config
Write-Host "[5/5] Configuring MCP file server..." -ForegroundColor Yellow

$projectPath = "C:\Users\perc7\Desktop\dev\43v3rMore"

# Convert Windows path to JSON-safe format
$jsonPath = $projectPath -replace '\\', '\\'

$config = @{
    mcpServers = @{
        filesystem = @{
            command = "npx"
            args = @(
                "-y"
                "@modelcontextprotocol/server-filesystem"
                $projectPath
            )
        }
    }
} | ConvertTo-Json -Depth 10

# Save config
$config | Out-File -FilePath $configPath -Encoding UTF8

Write-Host "✓ Configuration saved to: $configPath" -ForegroundColor Green

# Display configuration
Write-Host ""
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "  CONFIGURATION COMPLETE" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Config file location:" -ForegroundColor Yellow
Write-Host "  $configPath" -ForegroundColor White
Write-Host ""
Write-Host "Monitored directory:" -ForegroundColor Yellow
Write-Host "  $projectPath" -ForegroundColor White
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host $config -ForegroundColor White
Write-Host ""
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "  NEXT STEPS" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Close Claude Desktop completely (if open)" -ForegroundColor Yellow
Write-Host "2. Restart Claude Desktop" -ForegroundColor Yellow
Write-Host "3. Open a new conversation" -ForegroundColor Yellow
Write-Host "4. Ask Claude: 'List files in my 43v3rMore directory'" -ForegroundColor Yellow
Write-Host ""
Write-Host "✓ Setup complete! Claude can now access your files." -ForegroundColor Green
Write-Host ""

# Offer to open the project directory
$openDir = Read-Host "Would you like to open the project directory? (Y/N)"
if ($openDir -eq 'Y' -or $openDir -eq 'y') {
    if (Test-Path $projectPath) {
        Start-Process explorer.exe $projectPath
    } else {
        Write-Host "✗ Directory not found: $projectPath" -ForegroundColor Red
        Write-Host "Please update the path in this script and run again." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
