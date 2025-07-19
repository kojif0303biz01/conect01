"""
Azure CLI パスの問題を回避した直接認証テスト
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def test_azure_auth_direct():
    """Azure CLIのパス問題を回避した認証テスト"""
    print("=== 直接Azure認証テスト ===")
    
    # .env読み込み
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path, override=True)
    
    try:
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider
        from openai import AzureOpenAI
        
        print("DefaultAzureCredential を初期化中...")
        
        # Azure CLIの場所を明示的に指定
        os.environ["AZURE_CLI_PATH"] = r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
        
        credential = DefaultAzureCredential()
        
        print("Azure認証トークンを取得中...")
        token = credential.get_token("https://cognitiveservices.azure.com/.default")
        
        if token:
            print("OK Azure認証成功!")
            
            # Azure OpenAI接続テスト
            print("Azure OpenAI 接続テスト中...")
            
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
            
            # o3-pro簡単テスト
            print("\no3-pro テスト中...")
            response = client.responses.create(
                model="O3-pro",
                input="Azure CLI認証でテスト中です。1+1=?",
                reasoning={"effort": "low"}
            )
            print(f"OK o3-pro 成功: {response.output_text}")
            
            return True
            
        else:
            print("NG 認証トークン取得失敗")
            return False
            
    except Exception as e:
        print(f"NG Azure認証エラー: {e}")
        
        # エラーの詳細を分析
        error_str = str(e)
        if "AADSTS50020" in error_str:
            print("\n原因: 外部アカウントの制限")
            print("解決方法: 組織のAzure ADテナントにアカウントを追加")
        elif "AADSTS700016" in error_str:
            print("\n原因: アプリケーションが見つからない")
            print("解決方法: 正しいCLIENT_IDを設定、またはCLIENT_IDをコメントアウト")
        elif "DefaultAzureCredential failed" in error_str:
            print("\n原因: 複数の認証方法が失敗")
            print("解決方法: az login を実行して再ログイン")
        
        return False

def show_next_steps():
    """次のステップを表示"""
    print("\n=== 次のステップ ===")
    print("方法1（推奨）: 新しいPowerShellセッション")
    print("  1. 現在のPowerShellを閉じる")
    print("  2. 新しいPowerShellを開く")  
    print("  3. 仮想環境を再有効化")
    print("  4. az --version で確認")
    print("  5. python azure_cli_setup.py を実行")
    
    print("\n方法2: 手動パス修正")
    print("  PowerShellで以下を実行:")
    print("  $env:PATH += ';C:\\Program Files\\Microsoft SDKs\\Azure\\CLI2\\wbin'")
    print("  az --version")
    
    print("\n方法3: 直接CLIENT_IDを設定")
    print("  Azure Portalでアプリ登録を作成し、CLIENT_IDを.envに設定")

if __name__ == "__main__":
    print("Azure CLI パス問題回避テスト\n")
    
    success = test_azure_auth_direct()
    
    if success:
        print("\n SUCCESS Azure認証が正常に動作しています!")
        print("o3_pro_tester.py で Microsoft Entra ID認証を選択してください")
        
        # .envファイルのCLIENT_ID設定を確認
        env_path = Path(__file__).parent / ".env"
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "AZURE_CLIENT_ID=your-client-id" in content:
            print("\n注意: .envファイルのCLIENT_IDをコメントアウトすることを推奨")
            print("DefaultAzureCredential（Azure CLI認証）のみで動作するため")
    else:
        print("\n WARNING Azure認証に失敗しました")
        show_next_steps()