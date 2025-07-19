"""
Azure認証設定の確認と取得支援スクリプト
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def check_azure_auth_config():
    """Azure認証設定の確認"""
    
    # .envファイル読み込み
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path, override=True)
    
    print("=== Azure認証設定の確認 ===\n")
    
    # 現在の設定値を確認
    tenant_id = os.getenv("AZURE_TENANT_ID")
    client_id = os.getenv("AZURE_CLIENT_ID") 
    client_secret = os.getenv("AZURE_CLIENT_SECRET")
    
    print("現在の設定:")
    print(f"  AZURE_TENANT_ID: {tenant_id if tenant_id else '未設定'}")
    print(f"  AZURE_CLIENT_ID: {client_id if client_id else '未設定'}")
    print(f"  AZURE_CLIENT_SECRET: {'設定済み' if client_secret else '未設定'}")
    
    # テナントIDの妥当性チェック
    if tenant_id and len(tenant_id) == 36 and tenant_id.count('-') == 4:
        print("\nOK AZURE_TENANT_ID は正しい形式です")
    else:
        print("\nNG AZURE_TENANT_ID が正しくない可能性があります")
        print("  正しい形式: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
    
    return tenant_id, client_id, client_secret

def show_client_id_instructions():
    """AZURE_CLIENT_IDの取得手順を表示"""
    
    print(f"\n=== AZURE_CLIENT_ID の取得方法 ===")
    print("""
【方法1: Azure Portalでアプリ登録を作成】

1. Azure Portal (https://portal.azure.com) にログイン
2. 「Azure Active Directory」を検索・選択
3. 左メニューの「アプリの登録」をクリック
4. 「新規登録」をクリック
5. アプリケーション情報を入力:
   - 名前: 例「o3-pro-client」
   - サポートされているアカウントの種類: 「この組織ディレクトリのみ」
   - リダイレクト URI: 空欄でOK
6. 「登録」をクリック
7. 作成されたアプリの「概要」ページで以下を確認:
   - アプリケーション (クライアント) ID ← これがAZURE_CLIENT_ID
   - ディレクトリ (テナント) ID ← これがAZURE_TENANT_ID

【方法2: 既存のOpenAIリソースから確認】

1. Azure Portal で OpenAI リソースを開く
2. 左メニューの「アクセス制御 (IAM)」をクリック  
3. 「ロールの割り当て」タブを確認
4. 自分のアカウントが割り当てられている場合は、追加のアプリ登録は不要
5. この場合、DefaultAzureCredential() のみで認証可能

【方法3: Azure CLI で確認】

コマンドプロンプトで以下を実行:
```
az login
az account show
az ad sp list --display-name "your-app-name"
```
    """)

def test_default_credential():
    """DefaultAzureCredential のテスト"""
    
    print(f"\n=== DefaultAzureCredential テスト ===")
    
    try:
        from azure.identity import DefaultAzureCredential
        
        print("DefaultAzureCredential でテスト中...")
        credential = DefaultAzureCredential()
        
        # トークン取得テスト
        token = credential.get_token("https://cognitiveservices.azure.com/.default")
        
        if token:
            print("OK DefaultAzureCredential 認証成功!")
            print("CLIENT_IDとCLIENT_SECRETの設定は不要の可能性があります")
            print("az login または Visual Studio Code の Azure 拡張機能でログイン済みの場合")
            return True
        else:
            print("NG DefaultAzureCredential 認証失敗")
            return False
            
    except ImportError:
        print("NG azure-identity パッケージがインストールされていません")
        print("pip install azure-identity を実行してください")
        return False
    except Exception as e:
        print(f"NG DefaultAzureCredential エラー: {e}")
        print("明示的なCLIENT_IDとCLIENT_SECRETが必要です")
        return False

def test_azure_openai_auth():
    """Azure OpenAI認証のテスト"""
    
    print(f"\n=== Azure OpenAI 認証テスト ===")
    
    tenant_id, client_id, client_secret = check_azure_auth_config()
    
    # DefaultAzureCredential での認証テスト
    if test_default_credential():
        print("\n推奨: DefaultAzureCredential を使用")
        print("CLIENT_IDとCLIENT_SECRETの設定は不要です")
        
        # 実際にAzure OpenAIに接続テスト
        try:
            from azure.identity import DefaultAzureCredential, get_bearer_token_provider
            from openai import AzureOpenAI
            
            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(), 
                "https://cognitiveservices.azure.com/.default"
            )
            
            client = AzureOpenAI(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                azure_ad_token_provider=token_provider,
                api_version="2025-04-01-preview"
            )
            
            # 簡単なテスト
            models = client.models.list()
            print("OK Azure OpenAI 認証成功!")
            print(f"利用可能なモデル数: {len(models.data)}")
            return True
            
        except Exception as e:
            print(f"NG Azure OpenAI 認証失敗: {e}")
            return False
    
    else:
        print("\n明示的な CLIENT_ID と CLIENT_SECRET が必要です")
        return False

if __name__ == "__main__":
    print("Azure認証設定支援ツール\n")
    
    # 設定確認
    check_azure_auth_config()
    
    # 取得方法の説明
    show_client_id_instructions()
    
    # 認証テスト
    success = test_azure_openai_auth()
    
    if success:
        print(f"\n SUCCESS Azure認証設定完了!")
        print("o3_pro_tester.py で Microsoft Entra ID認証を選択してください")
    else:
        print(f"\n WARNING Azure認証の追加設定が必要です")
        print("上記の手順に従ってCLIENT_IDを取得してください")