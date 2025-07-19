"""
Azure認証トラブルシューティングツール

Azure CLI認証の問題を自動診断し、解決策を提示するツールです。

機能:
- Azure CLI インストール状況確認
- PATH環境変数の問題診断
- Azure ログイン状況確認
- DefaultAzureCredential の動作テスト
- 自動修復機能

使用方法:
python azure_auth_troubleshoot.py

作成日: 2025-01-19
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any


class AzureAuthDiagnostic:
    """Azure認証診断クラス"""
    
    def __init__(self):
        self.results: Dict[str, Any] = {}
        self.az_path: Optional[str] = None
    
    def run_full_diagnostic(self) -> Dict[str, Any]:
        """完全診断を実行"""
        print("=== Azure認証診断開始 ===\n")
        
        # 1. Azure CLI インストール確認
        self.check_azure_cli_installation()
        
        # 2. PATH環境変数確認
        self.check_path_environment()
        
        # 3. Azure CLI パス検索
        self.find_azure_cli_executable()
        
        # 4. Azure CLI バージョン確認
        self.test_azure_cli_version()
        
        # 5. Azure ログイン状況確認
        self.check_azure_login_status()
        
        # 6. Python Azure SDK確認
        self.check_azure_python_sdk()
        
        # 7. DefaultAzureCredential テスト
        self.test_default_azure_credential()
        
        # 8. 診断結果サマリー
        self.print_diagnostic_summary()
        
        # 9. 推奨解決策
        self.suggest_solutions()
        
        return self.results
    
    def check_azure_cli_installation(self):
        """Azure CLI インストール確認"""
        print("1. Azure CLI インストール確認")
        
        try:
            result = subprocess.run(['az', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version_info = result.stdout.split('\n')[0]
                print(f"   OK Azure CLI インストール済み: {version_info}")
                self.results['azure_cli_installed'] = True
                self.results['azure_cli_version'] = version_info
            else:
                print(f"   NG Azure CLI コマンドエラー: {result.stderr}")
                self.results['azure_cli_installed'] = False
                
        except FileNotFoundError:
            print("   NG Azure CLI が見つかりません（PATH問題の可能性）")
            self.results['azure_cli_installed'] = False
            self.results['azure_cli_path_issue'] = True
            
        except subprocess.TimeoutExpired:
            print("   NG Azure CLI コマンドタイムアウト")
            self.results['azure_cli_installed'] = False
            
        except Exception as e:
            print(f"   NG Azure CLI チェックエラー: {e}")
            self.results['azure_cli_installed'] = False
    
    def check_path_environment(self):
        """PATH環境変数確認"""
        print("\n2. PATH環境変数確認")
        
        path_env = os.environ.get('PATH', '')
        azure_paths = [p for p in path_env.split(';') 
                      if 'azure' in p.lower() or 'cli' in p.lower()]
        
        if azure_paths:
            print("   OK Azure関連のPATHが見つかりました:")
            for path in azure_paths:
                print(f"      {path}")
            self.results['azure_paths_in_env'] = azure_paths
        else:
            print("   WARN Azure関連のPATHが見つかりません")
            self.results['azure_paths_in_env'] = []
        
        # 一般的なAzure CLIパスをチェック
        common_paths = [
            r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin",
            r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin",
            f"C:\\Users\\{os.getenv('USERNAME')}\\AppData\\Local\\Programs\\Azure CLI\\wbin"
        ]
        
        existing_paths = [p for p in common_paths if os.path.exists(p)]
        if existing_paths:
            print("   INFO 既存のAzure CLIディレクトリ:")
            for path in existing_paths:
                print(f"      {path}")
                in_path = path in path_env
                print(f"        PATH設定済み: {'Yes' if in_path else 'No'}")
            self.results['existing_azure_dirs'] = existing_paths
    
    def find_azure_cli_executable(self):
        """Azure CLI実行ファイル検索"""
        print("\n3. Azure CLI実行ファイル検索")
        
        # shutil.which() で検索
        az_path = shutil.which('az')
        if az_path:
            print(f"   OK shutil.which()で発見: {az_path}")
            self.az_path = az_path
            self.results['azure_cli_path'] = az_path
            return
        
        # where コマンドで検索
        try:
            result = subprocess.run(['where', 'az'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                paths = result.stdout.strip().split('\n')
                print(f"   OK whereコマンドで発見: {paths[0]}")
                self.az_path = paths[0]
                self.results['azure_cli_path'] = paths[0]
                return
        except:
            pass
        
        # 手動検索
        common_executables = [
            r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
            r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
            f"C:\\Users\\{os.getenv('USERNAME')}\\AppData\\Local\\Programs\\Azure CLI\\wbin\\az.cmd"
        ]
        
        for exe_path in common_executables:
            if os.path.exists(exe_path):
                print(f"   OK 手動検索で発見: {exe_path}")
                self.az_path = exe_path
                self.results['azure_cli_path'] = exe_path
                return
        
        print("   NG Azure CLI実行ファイルが見つかりません")
        self.results['azure_cli_path'] = None
    
    def test_azure_cli_version(self):
        """Azure CLI バージョンテスト"""
        print("\n4. Azure CLI直接実行テスト")
        
        if not self.az_path:
            print("   SKIP Azure CLIパスが不明のためスキップ")
            return
        
        try:
            result = subprocess.run([self.az_path, '--version'], 
                                  capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                print("   OK Azure CLI直接実行成功")
                self.results['azure_cli_direct_works'] = True
            else:
                print(f"   NG Azure CLI直接実行失敗: {result.stderr}")
                self.results['azure_cli_direct_works'] = False
        except Exception as e:
            print(f"   NG Azure CLI直接実行エラー: {e}")
            self.results['azure_cli_direct_works'] = False
    
    def check_azure_login_status(self):
        """Azure ログイン状況確認"""
        print("\n5. Azure ログイン状況確認")
        
        if not self.az_path:
            print("   SKIP Azure CLIパスが不明のためスキップ")
            return
        
        try:
            result = subprocess.run([self.az_path, 'account', 'show'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                import json
                account_info = json.loads(result.stdout)
                user_name = account_info.get('user', {}).get('name', 'Unknown')
                tenant_id = account_info.get('tenantId', 'Unknown')
                print(f"   OK ログイン済み: {user_name}")
                print(f"      テナントID: {tenant_id}")
                self.results['azure_logged_in'] = True
                self.results['azure_user'] = user_name
                self.results['azure_tenant'] = tenant_id
            else:
                print("   NG ログインしていません")
                self.results['azure_logged_in'] = False
        except Exception as e:
            print(f"   NG ログイン確認エラー: {e}")
            self.results['azure_logged_in'] = False
    
    def check_azure_python_sdk(self):
        """Azure Python SDK確認"""
        print("\n6. Azure Python SDK確認")
        
        packages = {
            'azure.identity': 'Azure Identity SDK',
            'azure.ai.inference': 'Azure AI Inference SDK',
            'openai': 'OpenAI Python SDK'
        }
        
        for package, description in packages.items():
            try:
                __import__(package)
                print(f"   OK {description} インストール済み")
                self.results[f'{package}_installed'] = True
            except ImportError:
                print(f"   NG {description} 未インストール")
                self.results[f'{package}_installed'] = False
    
    def test_default_azure_credential(self):
        """DefaultAzureCredential テスト"""
        print("\n7. DefaultAzureCredential テスト")
        
        if not self.results.get('azure.identity_installed'):
            print("   SKIP azure.identity未インストールのためスキップ")
            return
        
        try:
            from azure.identity import DefaultAzureCredential
            from dotenv import load_dotenv
            
            # .env読み込み
            env_path = Path(__file__).parent / ".env"
            if env_path.exists():
                load_dotenv(env_path, override=True)
            
            print("   DefaultAzureCredential初期化中...")
            credential = DefaultAzureCredential()
            
            print("   認証トークン取得中...")
            token = credential.get_token("https://cognitiveservices.azure.com/.default")
            
            if token:
                print("   OK DefaultAzureCredential 成功!")
                self.results['default_azure_credential_works'] = True
                
                # Azure OpenAI接続テスト
                try:
                    from openai import AzureOpenAI
                    from azure.identity import get_bearer_token_provider
                    
                    token_provider = get_bearer_token_provider(
                        DefaultAzureCredential(),
                        "https://cognitiveservices.azure.com/.default"
                    )
                    
                    client = AzureOpenAI(
                        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                        azure_ad_token_provider=token_provider,
                        api_version="2025-04-01-preview"
                    )
                    
                    models = client.models.list()
                    print(f"   OK Azure OpenAI 接続成功（モデル数: {len(models.data)}）")
                    self.results['azure_openai_connection_works'] = True
                    
                except Exception as e:
                    print(f"   WARN Azure OpenAI接続失敗: {e}")
                    self.results['azure_openai_connection_works'] = False
            else:
                print("   NG トークン取得失敗")
                self.results['default_azure_credential_works'] = False
                
        except Exception as e:
            print(f"   NG DefaultAzureCredential エラー: {e}")
            self.results['default_azure_credential_works'] = False
            self.results['default_azure_credential_error'] = str(e)
    
    def print_diagnostic_summary(self):
        """診断結果サマリー表示"""
        print("\n" + "="*60)
        print("診断結果サマリー")
        print("="*60)
        
        checks = [
            ("Azure CLI インストール", "azure_cli_installed"),
            ("Azure CLI PATH設定", "azure_cli_path"),
            ("Azure CLI直接実行", "azure_cli_direct_works"), 
            ("Azure ログイン", "azure_logged_in"),
            ("Azure Identity SDK", "azure.identity_installed"),
            ("OpenAI SDK", "openai_installed"),
            ("DefaultAzureCredential", "default_azure_credential_works"),
            ("Azure OpenAI接続", "azure_openai_connection_works")
        ]
        
        for check_name, key in checks:
            if key in self.results:
                status = "OK" if self.results[key] else "NG"
                if key == "azure_cli_path":
                    status = "OK" if self.results[key] else "NG"
                print(f"{check_name:<25}: {status}")
            else:
                print(f"{check_name:<25}: SKIP")
    
    def suggest_solutions(self):
        """解決策提案"""
        print("\n" + "="*60)
        print("推奨解決策")
        print("="*60)
        
        issues = []
        
        # Azure CLIインストール問題
        if not self.results.get('azure_cli_installed'):
            if self.results.get('azure_cli_path_issue'):
                issues.append({
                    "problem": "Azure CLI はインストール済みだがPATH設定に問題",
                    "solutions": [
                        "PowerShellを再起動",
                        "install_azure_cli.ps1 を実行",
                        "fix_azure_path.ps1 を実行"
                    ]
                })
            else:
                issues.append({
                    "problem": "Azure CLI がインストールされていない",
                    "solutions": [
                        "install_azure_cli.ps1 を実行",
                        "https://docs.microsoft.com/cli/azure/install-azure-cli から手動インストール"
                    ]
                })
        
        # ログイン問題
        if not self.results.get('azure_logged_in'):
            issues.append({
                "problem": "Azureにログインしていない",
                "solutions": [
                    "az login を実行",
                    "azure_cli_setup.py を実行"
                ]
            })
        
        # Python SDK問題
        missing_packages = []
        for package in ['azure.identity', 'openai']:
            if not self.results.get(f'{package}_installed'):
                missing_packages.append(package.replace('.', '-'))
        
        if missing_packages:
            issues.append({
                "problem": f"必要なPythonパッケージが未インストール: {', '.join(missing_packages)}",
                "solutions": [
                    f"pip install {' '.join(missing_packages)}",
                    "pip install -r requirements.txt"
                ]
            })
        
        # DefaultAzureCredential問題
        if not self.results.get('default_azure_credential_works'):
            issues.append({
                "problem": "DefaultAzureCredential が動作しない",
                "solutions": [
                    "az login を再実行",
                    "PowerShellを管理者権限で実行",
                    ".envファイルのCLIENT_IDをコメントアウト",
                    "direct_azure_test.py を実行して詳細確認"
                ]
            })
        
        # 解決策表示
        if issues:
            for i, issue in enumerate(issues, 1):
                print(f"\n問題 {i}: {issue['problem']}")
                print("解決策:")
                for j, solution in enumerate(issue['solutions'], 1):
                    print(f"  {j}. {solution}")
        else:
            print("\nSUCCESS すべての診断項目が正常です！")
            print("Azure認証が正常に動作しています。")
    
    def auto_fix(self):
        """自動修復実行"""
        print("\n=== 自動修復実行 ===")
        
        # PATH修復
        if self.az_path and not self.results.get('azure_cli_installed'):
            print("Azure CLI PATHを修復中...")
            az_dir = os.path.dirname(self.az_path)
            current_path = os.environ.get('PATH', '')
            if az_dir not in current_path:
                os.environ['PATH'] = current_path + ';' + az_dir
                print(f"OK PATH に追加: {az_dir}")
                
                # 修復後テスト
                try:
                    subprocess.run(['az', '--version'], 
                                 capture_output=True, timeout=5)
                    print("OK PATH修復成功")
                except:
                    print("WARN PATH修復後もエラーが続いています")


def main():
    """メイン実行関数"""
    print("Azure認証トラブルシューティングツール")
    print("="*50)
    
    diagnostic = AzureAuthDiagnostic()
    results = diagnostic.run_full_diagnostic()
    
    # 自動修復オプション
    if not results.get('azure_cli_installed') and results.get('azure_cli_path'):
        print("\n自動修復を試行しますか？ (y/n): ", end="")
        if input().lower() == 'y':
            diagnostic.auto_fix()
    
    print("\n診断完了。詳細はターミナル出力を参照してください。")


if __name__ == "__main__":
    main()