. "$PSScriptRoot\01_set_env.ps1"

Write-Host "Listing landing objects (latest 50):" -ForegroundColor Cyan
aws s3 ls "s3://$env:S3_BUCKET/$env:S3_PREFIX/" --recursive | Select-Object -Last 50