# Load env vars
. "$PSScriptRoot\01_set_env.ps1"

# Sanity checks
python -c "import boto3; print('boto3 ok')" 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Host "boto3 not found. Run: pip install boto3" -ForegroundColor Red
  exit 1
}

Write-Host "Starting producer... (Ctrl+C to stop)" -ForegroundColor Green
python "$PSScriptRoot\..\producer\src\producer_s3.py"
