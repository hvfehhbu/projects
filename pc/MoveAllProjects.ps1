$sourcePath = "C:\Users\Administrator\Documents\Projects"
$destPath = "D:\Projects"

# Check if source exists
if (-not (Test-Path $sourcePath)) {
    Write-Error "Source directory not found: $sourcePath"
    exit 1
}

# Create destination directory if it doesn't exist
if (-not (Test-Path $destPath)) {
    Write-Host "Creating destination directory: $destPath"
    New-Item -ItemType Directory -Path $destPath -Force | Out-Null
}

Write-Host "Moving all contents from '$sourcePath' to '$destPath'..."

# Get all items in the source directory
$items = Get-ChildItem -Path $sourcePath

foreach ($item in $items) {
    # Skip the 'pc' folder initially to avoid issues if the script is running from there
    if ($item.Name -eq "pc") {
        Write-Host "Skipping 'pc' folder for now (will attempt to move last)..." -ForegroundColor Yellow
        continue
    }

    try {
        Write-Host "Moving: $($item.Name)"
        Move-Item -Path $item.FullName -Destination $destPath -Force -ErrorAction Stop
    } catch {
        Write-Error "Failed to move $($item.Name): $_"
    }
}

# Attempt to move 'pc' folder last
$pcPath = Join-Path $sourcePath "pc"
if (Test-Path $pcPath) {
    Write-Host "Attempting to move 'pc' folder..."
    try {
        Move-Item -Path $pcPath -Destination $destPath -Force -ErrorAction Stop
        Write-Host "'pc' folder moved successfully." -ForegroundColor Green
    } catch {
        Write-Warning "Could not move 'pc' folder. This is likely because the script is running from inside it."
        Write-Warning "Please move the 'pc' folder manually after this script finishes."
        Write-Warning "Error details: $_"
    }
}

Write-Host "Operation completed."
Write-Host "Please check '$destPath' to verify all files were moved."
