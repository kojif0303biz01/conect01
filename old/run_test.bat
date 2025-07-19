@echo off
echo === o3-pro Test Runner ===
echo.

REM 仮想環境の有効化
if exist venv\Scripts\activate.bat (
    echo 仮想環境を有効化中...
    call venv\Scripts\activate.bat
) else (
    echo Error: 仮想環境が見つかりません
    echo python -m venv venv を実行してください
    exit /b 1
)

REM 環境変数の表示（デバッグ用）
echo.
echo 環境変数チェック:
if defined AZURE_OPENAI_ENDPOINT (
    echo   AZURE_OPENAI_ENDPOINT: 設定済み
) else (
    echo   AZURE_OPENAI_ENDPOINT: 未設定
)

if defined AZURE_OPENAI_API_KEY (
    echo   AZURE_OPENAI_API_KEY: 設定済み
) else (
    echo   AZURE_OPENAI_API_KEY: 未設定
)

REM メインプログラムの実行
echo.
echo o3_pro_tester.py を実行中...
echo.
python src\o3_pro_tester.py

REM 実行結果の確認
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo エラーが発生しました。依存関係をインストールしてください:
    echo pip install -r requirements.txt
)

pause