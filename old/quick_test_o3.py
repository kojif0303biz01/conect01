"""
クイックo3-proテスト
仮想環境の問題を回避し、直接テストを実行
"""

import os
import sys
from pathlib import Path

# .envファイルの読み込み
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path, override=True)
    print(f".envファイル読み込み完了: {env_path}")
except ImportError:
    print("python-dotenvがインストールされていません")
    print("pip install python-dotenv を実行してください")
    sys.exit(1)

# OpenAI SDKのインポート
try:
    from openai import AzureOpenAI
    print("OpenAI SDK読み込み完了")
except ImportError:
    print("openaiがインストールされていません")
    print("pip install openai>=1.68.0 を実行してください")
    sys.exit(1)

def test_o3_pro():
    """o3-proの簡単なテスト"""
    
    # 環境変数確認
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    
    print(f"\n環境変数の状態:")
    print(f"  エンドポイント: {'設定済み' if endpoint else '未設定'}")
    print(f"  APIキー: {'設定済み' if api_key else '未設定'}")
    
    if not endpoint or not api_key:
        print("\nエラー: 環境変数が設定されていません")
        print(".envファイルを確認してください")
        return
    
    print(f"\nエンドポイント: {endpoint}")
    
    # クライアント作成
    try:
        client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version="2025-04-01-preview"
        )
        print("クライアント作成成功")
    except Exception as e:
        print(f"クライアント作成失敗: {e}")
        return
    
    # o3-proテスト（デプロイメント名のバリエーションを試す）
    deployment_names = ["O3-pro", "o3-pro", "o3-pro-2025-06-10"]
    
    for deployment in deployment_names:
        print(f"\n{deployment}でテスト中...")
        try:
            response = client.responses.create(
                model=deployment,
                input="簡単な質問: 1+1=?",
                reasoning={"effort": "low"}
            )
            print(f"成功! 回答: {response.output_text}")
            
            # より複雑な推論テスト
            print(f"\n複雑な推論テスト...")
            response2 = client.responses.create(
                model=deployment,
                input="なぜ空は青いのか、科学的に説明してください。",
                reasoning={"effort": "medium"}
            )
            print(f"回答: {response2.output_text[:200]}...")
            
            return True
            
        except Exception as e:
            print(f"  失敗: {e}")
            continue
    
    print("\nすべてのデプロイメント名で失敗しました")
    print("Azure AI Studioでデプロイメント名を確認してください")
    return False

if __name__ == "__main__":
    print("=== o3-pro クイックテスト ===\n")
    
    success = test_o3_pro()
    
    if success:
        print("\n✅ テスト成功!")
        print("\nメインプログラムを実行するには:")
        print("1. 仮想環境を有効化: venv\\Scripts\\activate")
        print("2. 依存関係インストール: pip install -r requirements.txt")
        print("3. 実行: python src\\o3_pro_tester.py")
    else:
        print("\n❌ テスト失敗")
        print("設定を確認してください")