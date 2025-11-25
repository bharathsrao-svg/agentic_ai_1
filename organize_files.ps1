# Script to organize Python files into directories
# Run with: .\organize_files.ps1

Write-Host "Organizing Python files..." -ForegroundColor Green

# Create directories
$dirs = @("tests", "scripts", "examples", "kite", "analysis")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "Created directory: $dir" -ForegroundColor Yellow
    }
}

# Move test files
Write-Host "`nMoving test files..." -ForegroundColor Cyan
Get-ChildItem -Filter "test_*.py" | ForEach-Object { 
    Move-Item $_.FullName -Destination "tests\" -ErrorAction SilentlyContinue
    Write-Host "  Moved: $($_.Name)" -ForegroundColor Gray
}
Get-ChildItem -Filter "*test*.py" | Where-Object { $_.Name -notlike "test_*" } | ForEach-Object {
    Move-Item $_.FullName -Destination "tests\" -ErrorAction SilentlyContinue
    Write-Host "  Moved: $($_.Name)" -ForegroundColor Gray
}

# Move utility scripts
Write-Host "`nMoving utility scripts..." -ForegroundColor Cyan
$scriptPatterns = @("*token*.py", "*setup*.py", "get_kite_*.py", "quick_*.py", "generate_*.py")
foreach ($pattern in $scriptPatterns) {
    Get-ChildItem -Filter $pattern | ForEach-Object {
        Move-Item $_.FullName -Destination "scripts\" -ErrorAction SilentlyContinue
        Write-Host "  Moved: $($_.Name)" -ForegroundColor Gray
    }
}

# Move examples
Write-Host "`nMoving example files..." -ForegroundColor Cyan
$examplePatterns = @("example_*.py", "simple_*.py", "*example*.py")
foreach ($pattern in $examplePatterns) {
    Get-ChildItem -Filter $pattern | ForEach-Object {
        Move-Item $_.FullName -Destination "examples\" -ErrorAction SilentlyContinue
        Write-Host "  Moved: $($_.Name)" -ForegroundColor Gray
    }
}

# Move Kite files
Write-Host "`nMoving Kite API files..." -ForegroundColor Cyan
if (Test-Path "mcp_kite_client.py") {
    Move-Item "mcp_kite_client.py" -Destination "kite\" -ErrorAction SilentlyContinue
    Write-Host "  Moved: mcp_kite_client.py" -ForegroundColor Gray
}
Get-ChildItem -Filter "kite_*.py" | ForEach-Object {
    Move-Item $_.FullName -Destination "kite\" -ErrorAction SilentlyContinue
    Write-Host "  Moved: $($_.Name)" -ForegroundColor Gray
}

# Move analysis files
Write-Host "`nMoving analysis files..." -ForegroundColor Cyan
Get-ChildItem -Filter "analyze_*.py" | ForEach-Object {
    Move-Item $_.FullName -Destination "analysis\" -ErrorAction SilentlyContinue
    Write-Host "  Moved: $($_.Name)" -ForegroundColor Gray
}

Write-Host "`nOrganization complete!" -ForegroundColor Green
Write-Host "`nRemaining Python files in root:" -ForegroundColor Yellow
Get-ChildItem -Filter "*.py" | Select-Object Name | Format-Table -AutoSize

