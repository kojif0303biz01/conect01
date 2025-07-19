# o3-pro Test Runner for PowerShell

Write-Host "=== o3-pro Test Runner ===" -ForegroundColor Cyan
Write-Host ""

# 仮想環境の有効化
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "仮想環境を有効化中..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "Error: 仮想環境が見つかりません" -ForegroundColor Red
    Write-Host "python -m venv venv を実行してください"
    exit 1
}

# 現在のディレクトリの確認
Write-Host ""
Write-Host "現在のディレクトリ: $(Get-Location)" -ForegroundColor Gray

# .envファイルの存在確認
if (Test-Path ".env") {
    Write-Host ".envファイル: 存在" -ForegroundColor Green
} else {
    Write-Host ".envファイル: 見つかりません" -ForegroundColor Red
}

# 依存関係のインストール確認
Write-Host ""
Write-Host "依存関係をチェック中..." -ForegroundColor Yellow
$packages = pip list | Select-String "openai|azure-identity|python-dotenv"
if ($packages) {
    Write-Host "必要なパッケージがインストール済み" -ForegroundColor Green
} else {
    Write-Host "依存関係をインストール中..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# メインプログラムの実行
Write-Host ""
Write-Host "o3_pro_tester.py を実行中..." -ForegroundColor Cyan
Write-Host ""

python src\o3_pro_tester.py

# 実行結果の確認
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "エラーが発生しました。" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")