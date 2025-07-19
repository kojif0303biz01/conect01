"""
環境変数デバッグ用スクリプト
.envファイルの読み込み状況を確認します
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def debug_environment():
    """環境変数の読み込み状況をデバッグ"""
    
    print("=== 環境変数デバッグ ===\n")
    
    # 現在の作業ディレクトリ
    current_dir = Path.cwd()
    print(f"現在の作業ディレクトリ: {current_dir}")
    
    # .envファイルの場所を確認
    env_file = current_dir / ".env"
    print(f".envファイルの場所: {env_file}")
    print(f".envファイルの存在: {env_file.exists()}")
    
    if env_file.exists():
        print(f".envファイルのサイズ: {env_file.stat().st_size} bytes")
        
        # .envファイルの内容を確認（APIキーは部分的にマスク）
        print("\n.envファイルの内容:")
        with open(env_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    # APIキーなどを部分的にマスク
                    if 'API_KEY' in line or 'SECRET' in line:
                        key, value = line.split('=', 1)
                        masked_value = value[:10] + '*' * (len(value) - 10) if len(value) > 10 else '*' * len(value)
                        print(f"  {i}: {key}={masked_value}")
                    else:
                        print(f"  {i}: {line}")
                elif line:
                    print(f"  {i}: {line}")
    
    # 明示的に.envファイルを読み込み
    print(f"\n.envファイルを読み込み中...")
    loaded = load_dotenv(env_file, verbose=True)
    print(f"load_dotenv()の結果: {loaded}")
    
    # 環境変数の確認
    print(f"\n=== Azure OpenAI環境変数の確認 ===")
    
    env_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT", 
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_DEPLOYMENT_NAME",
        "AZURE_AI_MODEL_NAME"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # APIキーの場合は部分的にマスク
            if 'API_KEY' in var:
                masked = value[:10] + '*' * (len(value) - 10) if len(value) > 10 else '*' * len(value)
                print(f"OK {var}: {masked}")
            else:
                print(f"OK {var}: {value}")
        else:
            print(f"NG {var}: 未設定")
    
    # 他の.envファイルも確認
    possible_locations = [
        Path.cwd().parent / ".env",
        Path.home() / ".env",
        Path(".") / ".env"
    ]
    
    print(f"\n=== 他の.envファイル場所の確認 ===")
    for location in possible_locations:
        if location.exists() and location != env_file:
            print(f"発見: {location}")
    
    return {
        "env_file_exists": env_file.exists(),
        "load_dotenv_result": loaded,
        "missing_vars": [var for var in env_vars if not os.getenv(var)]
    }

def test_azure_openai_connection():
    """Azure OpenAI接続をテスト"""
    
    print(f"\n=== Azure OpenAI接続テスト ===")
    
    # 環境変数再読み込み
    load_dotenv(override=True)
    
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    
    if not api_key:
        print("NG AZURE_OPENAI_API_KEY が設定されていません")
        return False
        
    if not endpoint:
        print("NG AZURE_OPENAI_ENDPOINT が設定されていません")
        return False
    
    try:
        from openai import AzureOpenAI
        
        client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version or "2025-04-01-preview"
        )
        
        print("OK AzureOpenAIクライアント作成成功")
        
        # モデル一覧を取得してテスト
        try:
            models = client.models.list()
            print("OK API接続成功")
            print(f"利用可能なモデル数: {len(models.data) if hasattr(models, 'data') else 'N/A'}")
            
            # o3-proモデルの確認
            model_names = [model.id for model in (models.data if hasattr(models, 'data') else [])]
            if any('o3' in name.lower() for name in model_names):
                print("OK o3モデル系が利用可能")
            else:
                print("! o3モデル系が見つかりません")
                print(f"利用可能なモデル: {model_names[:5]}")  # 最初の5個だけ表示
            
            return True
            
        except Exception as e:
            print(f"NG API接続失敗: {e}")
            return False
            
    except ImportError as e:
        print(f"NG OpenAIライブラリのインポート失敗: {e}")
        return False
    except Exception as e:
        print(f"NG クライアント作成失敗: {e}")
        return False

if __name__ == "__main__":
    try:
        # 環境変数デバッグ
        debug_result = debug_environment()
        
        # 接続テスト
        connection_success = test_azure_openai_connection()
        
        print(f"\n=== 診断結果 ===")
        print(f".envファイル存在: {debug_result['env_file_exists']}")
        print(f"環境変数読み込み成功: {debug_result['load_dotenv_result']}")
        print(f"不足している環境変数: {debug_result['missing_vars']}")
        print(f"Azure OpenAI接続: {'成功' if connection_success else '失敗'}")
        
        if debug_result['missing_vars']:
            print(f"\n⚠️  以下の環境変数を.envファイルに設定してください:")
            for var in debug_result['missing_vars']:
                print(f"   {var}=your-value-here")
                
    except Exception as e:
        print(f"デバッグ中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()