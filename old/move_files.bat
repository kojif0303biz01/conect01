@echo off
echo === プロジェクトファイル整理 ===

REM oldフォルダが存在しない場合は作成
if not exist "old" mkdir old

echo 途中過程のファイルをoldフォルダに移動中...

REM Azure診断・セットアップファイル
if exist "azure_cli_setup.py" move "azure_cli_setup.py" "old\" >nul
if exist "check_azure_auth.py" move "check_azure_auth.py" "old\" >nul
if exist "debug_azure_cli.py" move "debug_azure_cli.py" "old\" >nul
if exist "debug_env.py" move "debug_env.py" "old\" >nul
if exist "direct_azure_test.py" move "direct_azure_test.py" "old\" >nul

REM PowerShellスクリプト
if exist "fix_azure_path.ps1" move "fix_azure_path.ps1" "old\" >nul
if exist "install_azure_cli.ps1" move "install_azure_cli.ps1" "old\" >nul
if exist "organize_files.ps1" move "organize_files.ps1" "old\" >nul

REM テスト関連ファイル
if exist "test_failed_parts.py" move "test_failed_parts.py" "old\" >nul
if exist "quick_test_o3.py" move "quick_test_o3.py" "old\" >nul
if exist "simple_o3_test.py" move "simple_o3_test.py" "old\" >nul
if exist "run_test.bat" move "run_test.bat" "old\" >nul
if exist "run_test.ps1" move "run_test.ps1" "old\" >nul

REM テスト結果JSON
if exist "o3_pro_test_results_*.json" move "o3_pro_test_results_*.json" "old\" >nul 2>nul

REM その他ファイル
if exist "=1.68.0" del "=1.68.0" >nul

REM フォルダ移動
if exist "src" move "src" "old\" >nul
if exist "tests" move "tests" "old\" >nul
if exist "examples" move "examples" "old\" >nul

echo.
echo === 整理完了 ===
echo 以下のファイルがメインディレクトリに残りました:
dir /b *.py *.md *.txt *.env 2>nul

echo.
echo 整理作業が完了しました！
pause