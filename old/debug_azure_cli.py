"""
Azure CLI 認識問題のデバッグスクリプト
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def debug_environment():
    """環境変数とパスの確認"""
    print("=== 環境変数デバッグ ===")
    
    # PATH環境変数の確認
    path_env = os.environ.get('PATH', '')
    print(f"PATH環境変数の内容:")
    for path_item in path_env.split(';'):
        if 'azure' in path_item.lower() or 'cli' in path_item.lower():
            print(f"  Azure関連: {path_item}")
    
    print(f"\nPython実行環境: {sys.executable}")
    print(f"現在の作業ディレクトリ: {os.getcwd()}")

def find_azure_cli():
    """Azure CLIの場所を探す"""
    print("\n=== Azure CLI 検索 ===")
    
    # 一般的なインストール場所
    common_paths = [
        r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
        r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
        r"C:\Users\{}\AppData\Local\Programs\Azure CLI\wbin\az.cmd".format(os.getenv('USERNAME')),
        r"C:\Windows\System32\az.cmd",
        r"C:\Windows\az.cmd",
    ]
    
    print("一般的な場所を検索中...")
    for path in common_paths:
        if os.path.exists(path):
            print(f"発見: {path}")
            return path
    
    # shutil.which()で検索
    print("\nshutil.which()で検索中...")
    az_path = shutil.which('az')
    if az_path:
        print(f"発見: {az_path}")
        return az_path
    
    # where コマンドで検索
    print("\nwhereコマンドで検索中...")
    try:
        result = subprocess.run(['where', 'az'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            az_path = result.stdout.strip().split('\n')[0]
            print(f"発見: {az_path}")
            return az_path
    except Exception as e:
        print(f"where検索エラー: {e}")
    
    print("Azure CLI が見つかりません")
    return None

def test_azure_cli_direct():
    """Azure CLIの直接テスト"""
    print("\n=== Azure CLI 直接テスト ===")
    
    # まずazコマンドを探す
    az_path = find_azure_cli()
    
    if not az_path:
        print("Azure CLI の実行ファイルが見つかりません")
        return False
    
    # 直接実行テスト
    try:
        print(f"実行テスト: {az_path}")
        result = subprocess.run([az_path, '--version'], 
                              capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("OK Azure CLI 直接実行成功")
            print(f"出力: {result.stdout[:200]}...")
            return True
        else:
            print(f"NG Azure CLI 実行エラー: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("NG Azure CLI 実行タイムアウト")
        return False
    except Exception as e:
        print(f"NG Azure CLI 実行例外: {e}")
        return False

def test_different_commands():
    """異なるコマンド形式でテスト"""
    print("\n=== 異なるコマンド形式テスト ===")
    
    commands_to_try = [
        ['az', '--version'],
        ['az.cmd', '--version'],
        ['az.exe', '--version'],
        [r'C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd', '--version'],
        [r'C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd', '--version'],
    ]
    
    for cmd in commands_to_try:
        try:
            print(f"テスト: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"  OK 成功!")
                print(f"  バージョン: {result.stdout.split()[2] if len(result.stdout.split()) > 2 else 'Unknown'}")
                return cmd[0]  # 成功したコマンドを返す
            else:
                print(f"  NG 失敗: {result.stderr[:100]}")
                
        except FileNotFoundError:
            print(f"  NG ファイルが見つかりません")
        except subprocess.TimeoutExpired:
            print(f"  NG タイムアウト")
        except Exception as e:
            print(f"  NG エラー: {e}")
    
    return None

def fix_azure_cli_path():
    """Azure CLIのパス問題を修正"""
    print("\n=== パス問題の修正 ===")
    
    # Azure CLIを見つける
    az_path = find_azure_cli()
    
    if az_path:
        # パスのディレクトリ部分を取得
        az_dir = os.path.dirname(az_path)
        print(f"Azure CLIディレクトリ: {az_dir}")
        
        # 現在のPATHに追加
        current_path = os.environ.get('PATH', '')
        if az_dir not in current_path:
            print("PATHに追加中...")
            os.environ['PATH'] = current_path + ';' + az_dir
            
            # テスト
            try:
                result = subprocess.run(['az', '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print("OK パス修正成功")
                    return True
            except:
                pass
        
        print("パス修正が必要な場合があります")
        print(f"手動でPATHに追加: {az_dir}")
        
    return False

def test_azure_auth_after_fix():
    """修正後のAzure認証テスト"""
    print("\n=== 修正後認証テスト ===")
    
    try:
        from azure.identity import DefaultAzureCredential
        from dotenv import load_dotenv
        
        # .env読み込み
        env_path = Path(__file__).parent / ".env"
        load_dotenv(env_path, override=True)
        
        print("DefaultAzureCredential でテスト中...")
        credential = DefaultAzureCredential()
        
        # トークン取得テスト
        token = credential.get_token("https://cognitiveservices.azure.com/.default")
        
        if token:
            print("OK Azure認証成功!")
            print("CLIENT_IDとCLIENT_SECRETは不要です")
            
            # Azure OpenAI接続テスト
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
            print("OK Azure OpenAI 接続成功!")
            print(f"利用可能なモデル数: {len(models.data)}")
            return True
            
        else:
            print("NG 認証トークン取得失敗")
            return False
            
    except Exception as e:
        print(f"NG 認証テスト失敗: {e}")
        return False

if __name__ == "__main__":
    print("=== Azure CLI 認識問題デバッグ ===\n")
    
    # 環境デバッグ
    debug_environment()
    
    # Azure CLI検索とテスト
    successful_cmd = test_different_commands()
    
    if successful_cmd:
        print(f"\n成功コマンド: {successful_cmd}")
        
        # パス修正
        fix_azure_cli_path()
        
        # 認証テスト
        if test_azure_auth_after_fix():
            print(f"\n SUCCESS Azure CLI認証が正常に動作しています!")
            print("o3_pro_tester.py で Microsoft Entra ID認証を選択してください")
        else:
            print(f"\n WARNING 認証テストに失敗しました")
    else:
        print(f"\n ERROR Azure CLI が正常に動作していません")
        print("Azure CLI を再インストールしてください")
        print("または、PowerShell/コマンドプロンプトを再起動してください")