# ファイル整理スクリプト - 不要な途中ファイルをoldフォルダに移動

Write-Host "=== プロジェクトファイル整理 ===" -ForegroundColor Cyan

# oldフォルダが存在しない場合は作成
if (-not (Test-Path "old")) {
    New-Item -ItemType Directory -Name "old"
    Write-Host "oldフォルダを作成しました" -ForegroundColor Green
}

# 移動するファイルのリスト（途中過程のファイル）
$filesToMove = @(
    # Azure診断・セットアップファイル
    "azure_cli_setup.py",
    "check_azure_auth.py", 
    "debug_azure_cli.py",
    "debug_env.py",
    "direct_azure_test.py",
    
    # PowerShellスクリプト
    "fix_azure_path.ps1",
    "install_azure_cli.ps1",
    
    # テスト関連
    "test_failed_parts.py",
    "quick_test_o3.py", 
    "simple_o3_test.py",
    "run_test.bat",
    "run_test.ps1",
    
    # テスト結果JSON
    "o3_pro_test_results_*.json",
    
    # その他の一時ファイル
    "=1.68.0"
)

# フォルダを移動
$foldersToMove = @(
    "src",
    "tests", 
    "examples"
)

Write-Host "途中過程のファイルを old フォルダに移動中..." -ForegroundColor Yellow

# ファイル移動
foreach ($file in $filesToMove) {
    if ($file -like "*.*") {
        # ワイルドカードを含む場合
        $matches = Get-ChildItem -Name $file -ErrorAction SilentlyContinue
        foreach ($match in $matches) {
            if (Test-Path $match) {
                Move-Item $match "old\" -Force
                Write-Host "  移動: $match" -ForegroundColor Gray
            }
        }
    } else {
        # 通常のファイル
        if (Test-Path $file) {
            Move-Item $file "old\" -Force
            Write-Host "  移動: $file" -ForegroundColor Gray
        }
    }
}

# フォルダ移動
foreach ($folder in $foldersToMove) {
    if (Test-Path $folder) {
        Move-Item $folder "old\" -Force
        Write-Host "  移動: $folder\" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "=== 整理完了 ===" -ForegroundColor Green
Write-Host "メインディレクトリに残ったファイル:" -ForegroundColor Cyan

# 最終的に残ったファイル一覧表示
Get-ChildItem -File | ForEach-Object {
    Write-Host "  ✓ $($_.Name)" -ForegroundColor Green
}

Write-Host ""
Write-Host "移動されたファイル（oldフォルダ）:" -ForegroundColor Yellow
Get-ChildItem "old" -Recurse | ForEach-Object {
    Write-Host "  → old\$($_.Name)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "整理作業が完了しました！" -ForegroundColor Green