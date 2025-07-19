# Azure CLI パス修正スクリプト

Write-Host "=== Azure CLI パス修正 ===" -ForegroundColor Cyan

# Azure CLIの一般的なパス
$azurePaths = @(
    "C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin",
    "C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin"
)

foreach ($path in $azurePaths) {
    if (Test-Path $path) {
        Write-Host "Azure CLIディレクトリ発見: $path" -ForegroundColor Green
        
        # 現在のセッションのPATHに追加
        $env:PATH = $env:PATH + ";" + $path
        
        # テスト実行
        try {
            $result = az --version 2>$null
            if ($result) {
                Write-Host "OK Azure CLI 動作確認成功" -ForegroundColor Green
                Write-Host $result[0]
                
                # 永続的にPATHを設定
                $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
                if ($userPath -notlike "*$path*") {
                    [Environment]::SetEnvironmentVariable("PATH", $userPath + ";" + $path, "User")
                    Write-Host "ユーザーPATHに永続的に追加しました" -ForegroundColor Yellow
                }
                
                break
            }
        } catch {
            Write-Host "このパスでは動作しませんでした: $path" -ForegroundColor Red
        }
    }
}

# 最終確認
Write-Host ""
Write-Host "最終確認..." -ForegroundColor Yellow
try {
    az --version
    Write-Host "Azure CLI が正常に動作しています" -ForegroundColor Green
} catch {
    Write-Host "まだ問題があります。PowerShellを再起動してください" -ForegroundColor Red
}