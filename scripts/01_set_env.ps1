# ---- Edit these ----
$env:AWS_REGION="eu-north-1"
$env:S3_BUCKET="lej7-s3-databricks-realtime-04140428"
$env:S3_PREFIX="landing/clickstream"
$env:BATCH_SECONDS="5"
$env:ROWS_PER_BATCH="50"

Write-Host "Environment set:"
Write-Host "  AWS_REGION=$env:AWS_REGION"
Write-Host "  S3_BUCKET=$env:S3_BUCKET"
Write-Host "  S3_PREFIX=$env:S3_PREFIX"
Write-Host "  BATCH_SECONDS=$env:BATCH_SECONDS"
Write-Host "  ROWS_PER_BATCH=$env:ROWS_PER_BATCH"
