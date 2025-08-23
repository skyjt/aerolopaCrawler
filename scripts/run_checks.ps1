Param(
    [switch]$Install
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($Install) {
    if (-not (Test-Path .venv)) {
        python -m venv .venv
    }
    . .\.venv\Scripts\Activate.ps1
    if (Test-Path requirements.txt) {
        pip install -r requirements.txt
    }
    if (Test-Path requirements-dev.txt) {
        pip install -r requirements-dev.txt
    } else {
        pip install pytest pytest-cov black ruff mypy
    }
} else {
    if (-not (Test-Path .\.venv\Scripts\Activate.ps1)) {
        Write-Error "Virtualenv not found. Run with -Install to create and install deps."
        exit 1
    }
    . .\.venv\Scripts\Activate.ps1
}

Write-Host "Running ruff..."
ruff check .

Write-Host "Running black (check)..."
black --check .

Write-Host "Running mypy..."
mypy src

Write-Host "Running tests with coverage..."
pytest --cov=src --cov-report=term-missing -q

