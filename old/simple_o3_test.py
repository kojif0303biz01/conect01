"""
シンプルなo3-proテストプログラム
環境変数の読み込み問題を解決し、基本的な接続テストを行います
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from openai import AzureOpenAI

# 環境変数の明示的読み込み
env_file = Path(__file__).parent / ".env"
load_dotenv(env_file, override=True)

def test_basic_connection():
    """基本的な接続テスト"""
    print("=== シンプルなo3-pro接続テスト ===\n")
    
    # 環境変数確認
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview")
    
    print(f"エンドポイント: {endpoint}")
    print(f"APIバージョン: {api_version}")
    print(f"APIキー: {'設定済み' if api_key else '未設定'}")
    
    if not api_key or not endpoint:
        print("\nエラー: API KeyまたはEndpointが設定されていません")
        return False
    
    try:
        # クライアント作成
        client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version
        )
        
        print("\nOK クライアント作成成功")
        
        # モデル一覧の取得
        try:
            models = client.models.list()
            model_names = [model.id for model in models.data]
            print(f"OK 利用可能なモデル数: {len(model_names)}")
            
            # o3関連モデルの確認
            o3_models = [name for name in model_names if 'o3' in name.lower()]
            if o3_models:
                print(f"OK o3モデル系: {o3_models}")
            else:
                print("! o3モデルが見つかりません")
                print(f"利用可能なモデルの一部: {model_names[:10]}")
            
        except Exception as e:
            print(f"NG モデル一覧取得失敗: {e}")
            return False
        
        # 新しいResponses APIのテスト
        print(f"\n=== Responses APIテスト ===")
        
        # まず従来のChat Completions APIで試してみる
        try:
            print("Chat Completions APIでテスト中...")
            response = client.chat.completions.create(
                model="gpt-4o",  # 一般的なモデルでテスト
                messages=[
                    {"role": "user", "content": "簡単なテスト: 2+2=?"}
                ],
                max_tokens=50
            )
            print(f"OK Chat Completions API成功: {response.choices[0].message.content}")
            
        except Exception as e:
            print(f"Chat Completions API失敗: {e}")
        
        # Responses APIのテスト
        try:
            print("\nResponses APIでテスト中...")
            
            # まずは一般的なモデルで試す
            available_models = ["gpt-4o", "gpt-4", "gpt-35-turbo"]
            
            for model in available_models:
                if model in model_names or any(model in name for name in model_names):
                    try:
                        response = client.responses.create(
                            model=model,
                            input="簡単なテスト: 1+1=?"
                        )
                        print(f"OK Responses API成功 ({model}): {response.output_text[:100]}...")
                        break
                    except Exception as e:
                        print(f"  {model}で失敗: {e}")
                        continue
            else:
                print("! 利用可能なモデルでResponses APIが動作しませんでした")
            
        except Exception as e:
            print(f"Responses API失敗: {e}")
        
        # o3-proモデルの直接テスト
        print(f"\n=== o3-proモデル直接テスト ===")
        
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "o3-pro")
        print(f"デプロイメント名: {deployment_name}")
        
        try:
            response = client.responses.create(
                model=deployment_name,
                input="簡単な推論テスト: 2の平方根は無理数ですか？",
                reasoning={"effort": "low"}
            )
            print(f"OK o3-pro成功: {response.output_text[:200]}...")
            return True
            
        except Exception as e:
            print(f"o3-pro失敗: {e}")
            
            # デプロイメント名のバリエーションを試す
            variations = ["o3-pro", "O3-pro", "o3pro", "O3pro"]
            for variant in variations:
                if variant != deployment_name:
                    try:
                        print(f"  {variant}で再試行中...")
                        response = client.responses.create(
                            model=variant,
                            input="テスト",
                            reasoning={"effort": "low"}
                        )
                        print(f"OK {variant}で成功!")
                        return True
                    except Exception as e2:
                        print(f"  {variant}も失敗: {e2}")
            
            return False
        
    except Exception as e:
        print(f"NG クライアント作成失敗: {e}")
        return False

def test_with_different_endpoints():
    """異なるエンドポイント形式でテスト"""
    print(f"\n=== 異なるエンドポイント形式でのテスト ===")
    
    base_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    
    if not base_endpoint or not api_key:
        print("基本的な環境変数が設定されていません")
        return
    
    # 異なるエンドポイント形式を試す
    endpoint_variations = [
        base_endpoint,
        base_endpoint.rstrip('/'),
        base_endpoint + ('/' if not base_endpoint.endswith('/') else '')
    ]
    
    for i, endpoint in enumerate(endpoint_variations, 1):
        print(f"\n{i}. エンドポイント: {endpoint}")
        
        try:
            client = AzureOpenAI(
                api_key=api_key,
                azure_endpoint=endpoint,
                api_version="2025-04-01-preview"
            )
            
            # 簡単な接続テスト
            models = client.models.list()
            print(f"  OK 接続成功 ({len(models.data)}モデル)")
            
        except Exception as e:
            print(f"  NG 接続失敗: {e}")

if __name__ == "__main__":
    success = test_basic_connection()
    test_with_different_endpoints()
    
    if success:
        print(f"\n SUCCESS o3-proテスト成功! メインのテストプログラムを実行できます。")
        print("次のコマンドを実行してください:")
        print("python src/o3_pro_tester.py")
    else:
        print(f"\n WARNING o3-proモデルの設定を確認してください:")
        print("1. Azure AI StudioでO3-proモデルがデプロイされているか確認")
        print("2. デプロイメント名が正しく設定されているか確認")
        print("3. APIバージョンが対応しているか確認")