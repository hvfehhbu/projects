# Check if D: drive exists
if (-not (Test-Path "D:\")) {
    Write-Error "Drive D:\ does not exist. Please ensure the drive is mounted and try again."
    exit 1
}

$sourcePath = "$env:USERPROFILE\Downloads"
$destPath = "D:\Downloads"

# Create destination directory if it doesn't exist
if (-not (Test-Path $destPath)) {
    Write-Host "Creating destination directory: $destPath"
    New-Item -ItemType Directory -Path $destPath -Force | Out-Null
}

# Move files
if (Test-Path $sourcePath) {
    Write-Host "Moving files from $sourcePath to $destPath..."
    # Move all items from source to destination
    Get-ChildItem -Path $sourcePath | Move-Item -Destination $destPath -Force
    Write-Host "Files moved successfully."
} else {
    Write-Warning "Source Downloads folder not found at $sourcePath"
}

# Update Registry for "User Shell Folders"
$regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
$downloadsGuid = "{374DE290-123F-4565-9164-39C4925E467B}"

Write-Host "Updating Registry..."
Set-ItemProperty -Path $regPath -Name $downloadsGuid -Value $destPath -Type ExpandString

# Update Registry for "Shell Folders" (Legacy but good to have)
$regPathLegacy = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
Set-ItemProperty -Path $regPathLegacy -Name $downloadsGuid -Value $destPath -Type String

Write-Host "Registry updated."
Write-Host "The Downloads folder location has been changed to $destPath."
Write-Host "You may need to restart Windows Explorer or sign out and sign back in for the changes to fully take effect."
Write-Host "Done."
