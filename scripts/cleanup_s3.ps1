. "$PSScriptRoot\01_set_env.ps1"

Write-Host "This will DELETE demo data under:" -ForegroundColor Yellow
Write-Host "  s3://$env:S3_BUCKET/landing/" -ForegroundColor Yellow
Write-Host "  s3://$env:S3_BUCKET/delta/" -ForegroundColor Yellow
Write-Host "  s3://$env:S3_BUCKET/checkpoints/" -ForegroundColor Yellow
$confirm = Read-Host "Type DELETE to continue"
if ($confirm -ne "DELETE") {
  Write-Host "Cancelled." -ForegroundColor Green
  exit 0
}

aws s3 rm "s3://$env:S3_BUCKET/landing/" --recursive
aws s3 rm "s3://$env:S3_BUCKET/delta/" --recursive
aws s3 rm "s3://$env:S3_BUCKET/checkpoints/" --recursive

Write-Host "Cleanup complete." -ForegroundColor Green
