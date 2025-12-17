$directoriesToRemove = @(
    "web/node_modules",
    "web/dist",
    "backend/__pycache__",
    "backend/strategies/__pycache__",
    "backend/core/__pycache__",
    "backend/routers/__pycache__",
    "backend/utils/__pycache__",
    "backend/.pytest_cache",
    ".idea",
    ".vscode"
)

# Function to remove directory recursively
function Remove-Directory($path) {
    if (Test-Path $path) {
        Write-Host "Removing $path..." -ForegroundColor Yellow
        Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "Removed $path" -ForegroundColor Green
    } else {
        Write-Host "Skipping $path (not found)" -ForegroundColor Gray
    }
}

# Remove specific lists
foreach ($dir in $directoriesToRemove) {
    Remove-Directory $dir
}

# Recursively remove all __pycache__ folders
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | ForEach-Object {
    Remove-Directory $_.FullName
}

Write-Host "Cleanup Complete! You can now zip the folder." -ForegroundColor Cyan
