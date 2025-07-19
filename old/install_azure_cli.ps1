# Azure CLI インストールスクリプト（PowerShell）

Write-Host "=== Azure CLI インストール ===" -ForegroundColor Cyan
Write-Host ""

# 管理者権限チェック
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "注意: 管理者権限で実行することを推奨します" -ForegroundColor Yellow
    Write-Host "PowerShellを右クリック → '管理者として実行' を選択してください" -ForegroundColor Yellow
    Write-Host ""
}

# 既存インストールチェック
Write-Host "既存のAzure CLIをチェック中..." -ForegroundColor Yellow
try {
    $version = az --version 2>$null
    if ($version) {
        Write-Host "Azure CLI は既にインストールされています" -ForegroundColor Green
        Write-Host $version[0]
        $update = Read-Host "最新版にアップデートしますか？ (y/n)"
        if ($update -ne 'y') {
            exit 0
        }
    }
} catch {
    Write-Host "Azure CLI はインストールされていません" -ForegroundColor Red
}

Write-Host ""
Write-Host "インストール方法を選択してください:" -ForegroundColor Cyan
Write-Host "1. MSI インストーラー（推奨・簡単）"
Write-Host "2. winget（Windows Package Manager）"
Write-Host "3. PowerShell（コマンドライン）"
Write-Host "4. 手動ダウンロード"

$choice = Read-Host "選択 (1-4)"

switch ($choice) {
    "1" {
        Write-Host "MSI インストーラーでインストール中..." -ForegroundColor Yellow
        
        # MSIファイルのダウンロード
        $url = "https://aka.ms/installazurecliwindows"
        $output = "$env:TEMP\AzureCLI.msi"
        
        Write-Host "ダウンロード中: $url" -ForegroundColor Gray
        try {
            Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing
            Write-Host "ダウンロード完了" -ForegroundColor Green
            
            # MSIインストール実行
            Write-Host "インストーラーを起動中..." -ForegroundColor Yellow
            Start-Process msiexec.exe -ArgumentList "/i `"$output`" /quiet /norestart" -Wait -Verb RunAs
            
            Write-Host "インストール完了" -ForegroundColor Green
            
            # 一時ファイル削除
            Remove-Item $output -Force
            
        } catch {
            Write-Host "エラー: ダウンロードに失敗しました" -ForegroundColor Red
            Write-Host $_.Exception.Message -ForegroundColor Red
        }
    }
    
    "2" {
        Write-Host "winget でインストール中..." -ForegroundColor Yellow
        
        try {
            winget install -e --id Microsoft.AzureCLI
            Write-Host "winget インストール完了" -ForegroundColor Green
        } catch {
            Write-Host "エラー: winget が利用できません" -ForegroundColor Red
            Write-Host "Windows 10 バージョン 1809 以降または Windows 11 が必要です" -ForegroundColor Yellow
        }
    }
    
    "3" {
        Write-Host "PowerShell でインストール中..." -ForegroundColor Yellow
        
        try {
            # PowerShell スクリプトでインストール
            $ProgressPreference = 'SilentlyContinue'
            Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\AzureCLI.msi
            Start-Process msiexec.exe -Wait -ArgumentList '/I AzureCLI.msi /quiet'
            Remove-Item .\AzureCLI.msi
            
            Write-Host "PowerShell インストール完了" -ForegroundColor Green
        } catch {
            Write-Host "エラー: PowerShell インストールに失敗しました" -ForegroundColor Red
            Write-Host $_.Exception.Message -ForegroundColor Red
        }
    }
    
    "4" {
        Write-Host "手動ダウンロードページを開きます..." -ForegroundColor Yellow
        Start-Process "https://docs.microsoft.com/cli/azure/install-azure-cli-windows"
        Write-Host "ブラウザでダウンロードページが開きました" -ForegroundColor Green
        Write-Host "MSI ファイルをダウンロードして実行してください" -ForegroundColor Yellow
    }
    
    default {
        Write-Host "無効な選択です" -ForegroundColor Red
        exit 1
    }
}

# インストール確認
Write-Host ""
Write-Host "インストール確認中..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# パスの更新（新しいPowerShellセッションをシミュレート）
$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")

try {
    $version = az --version 2>$null
    if ($version) {
        Write-Host ""
        Write-Host "✓ Azure CLI インストール成功!" -ForegroundColor Green
        Write-Host $version[0] -ForegroundColor Green
        Write-Host ""
        Write-Host "次のステップ:" -ForegroundColor Cyan
        Write-Host "1. PowerShell/コマンドプロンプトを再起動"
        Write-Host "2. 'az login' でAzureにログイン" 
        Write-Host "3. 'python azure_cli_setup.py' で認証テスト"
    } else {
        Write-Host ""
        Write-Host "⚠ インストールは完了しましたが、パスの更新が必要です" -ForegroundColor Yellow
        Write-Host "PowerShell/コマンドプロンプトを再起動してください" -ForegroundColor Yellow
    }
} catch {
    Write-Host ""
    Write-Host "⚠ インストール確認に失敗しました" -ForegroundColor Yellow
    Write-Host "PowerShell/コマンドプロンプトを再起動してから 'az --version' を実行してください" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")