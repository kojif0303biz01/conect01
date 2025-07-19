@echo off
echo ファイル移動開始...

move "check_azure_auth.py" "old\" 2>nul
move "debug_azure_cli.py" "old\" 2>nul  
move "debug_env.py" "old\" 2>nul
move "direct_azure_test.py" "old\" 2>nul
move "fix_azure_path.ps1" "old\" 2>nul
move "install_azure_cli.ps1" "old\" 2>nul
move "organize_files.ps1" "old\" 2>nul
move "test_failed_parts.py" "old\" 2>nul
move "quick_test_o3.py" "old\" 2>nul
move "simple_o3_test.py" "old\" 2>nul
move "run_test.bat" "old\" 2>nul
move "run_test.ps1" "old\" 2>nul
move "move_files.bat" "old\" 2>nul
move "organize_project.py" "old\" 2>nul
move "simple_cleanup.py" "old\" 2>nul
del "=1.68.0" 2>nul

echo JSONファイル移動...
move "o3_pro_test_results_*.json" "old\" 2>nul

echo フォルダ移動...
move "src" "old\" 2>nul
move "tests" "old\" 2>nul  
move "examples" "old\" 2>nul

echo 移動完了
dir /b
echo.
echo oldフォルダ内容:
dir /b old\