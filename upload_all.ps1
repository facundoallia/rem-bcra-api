# Upload all JSON files to R2 using wrangler
$env:PATH = "$env:APPDATA\npm;$env:PATH"
$env:CLOUDFLARE_API_TOKEN = "KbOWrNs3a0VEL0F8AC98_6DE_tyIk9WO-jJtrYNz"
$env:CLOUDFLARE_ACCOUNT_ID = "b716491d6afe361dba0e016519df6cb3"
$env:NODE_TLS_REJECT_UNAUTHORIZED = "0"

$bucket = "rem-data"
$dataDir = "C:\Desarrollos\api REM\data"

Write-Host "=" * 70
Write-Host "Subiendo archivos JSON a R2..."
Write-Host "=" * 70
Write-Host ""

$files = Get-ChildItem -Path $dataDir -Filter "rem_*.json"

$success = 0
$failed = 0

foreach ($file in $files) {
    $objectKey = "data/$($file.Name)"
    Write-Host "Subiendo $($file.Name)... " -NoNewline
    
    try {
        wrangler r2 object put "$bucket/$objectKey" --file="$($file.FullName)" | Out-Null
        Write-Host "✅" -ForegroundColor Green
        $success++
    }
    catch {
        Write-Host "❌" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Write-Host "=" * 70
Write-Host "Exitosos: $success"
Write-Host "Fallidos: $failed"
Write-Host "=" * 70
