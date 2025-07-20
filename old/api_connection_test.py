#!/usr/bin/env python3
"""
API接続テストスクリプト

作成したモジュールを使用してAzure OpenAI o3-proとの実際の接続をテストします。
非対話モードで自動実行されます。

実行方法:
    source venv/bin/activate && python api_connection_test.py

作成日: 2025-07-19
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.azure_auth import O3ProConfig, O3ProClient
from core.error_handler import ErrorHandler, safe_api_call
from handlers import ReasoningHandler, StreamingHandler


def test_api_connection():
    """API接続テスト"""
    print("=" * 60)
    print("Azure OpenAI o3-pro API接続テスト開始")
    print("=" * 60)
    
    try:
        # 設定とクライアント初期化
        print("\n=== 設定とクライアント初期化 ===")
        config = O3ProConfig()
        
        if not config.validate():
            print("NG 設定が不正です")
            return False
        
        print(f"OK エンドポイント: {config.endpoint}")
        print(f"OK デプロイメント: {config.deployment}")
        print(f"OK API バージョン: {config.api_version}")
        
        # クライアント初期化（API Key優先）
        client = O3ProClient(config, auth_method="api_key")
        
        if not client.is_ready():
            print("NG クライアント初期化失敗")
            return False
        
        print("OK クライアント初期化成功")
        
        # 基本推論テスト
        print("\n=== 基本推論テスト（lowレベル） ===")
        reasoning_handler = ReasoningHandler(client)
        
        test_question = "2+2の計算結果を教えてください"
        result = reasoning_handler.basic_reasoning(test_question, effort="low")
        
        if result["success"]:
            print("OK 基本推論テスト成功")
            print(f"   質問: {test_question}")
            print(f"   回答: {result['response'][:100]}...")
            print(f"   実行時間: {result['duration']:.1f}秒")
        else:
            print(f"NG 基本推論テスト失敗: {result.get('error')}")
            return False
        
        # エラーハンドリング機能テスト
        print("\n=== エラーハンドリング機能テスト ===")
        error_handler = ErrorHandler(max_retries=1)
        
        # 正常なAPI呼び出しテスト
        api_params = {
            "model": config.deployment,
            "input": "簡単な質問: 1+1は？",
            "reasoning": {"effort": "low"}
        }
        
        result = error_handler.handle_api_call(client.client, **api_params)
        
        if hasattr(result, 'output_text'):
            print("OK エラーハンドリング機能テスト成功")
            print(f"   回答: {result.output_text[:100]}...")
        else:
            print(f"NG エラーハンドリング機能テスト失敗: {result}")
            return False
        
        # ストリーミングテスト（短時間）
        print("\n=== ストリーミングテスト ===")
        streaming_handler = StreamingHandler(client)
        
        stream_result = streaming_handler.stream_response("日本の首都は？", effort="low")
        
        if stream_result["success"]:
            print("OK ストリーミングテスト成功")
            print(f"   チャンク数: {stream_result['chunk_count']}")
            print(f"   実行時間: {stream_result['duration']:.1f}秒")
        else:
            print(f"NG ストリーミングテスト失敗: {stream_result.get('error')}")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 全てのAPI接続テストが成功しました！")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\nERROR API接続テスト中に予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_safe_api_call():
    """safe_api_call関数の単体テスト"""
    print("\n=== safe_api_call関数テスト ===")
    
    try:
        config = O3ProConfig()
        client = O3ProClient(config, auth_method="api_key")
        
        if not client.is_ready():
            print("クライアント初期化失敗のためテストをスキップ")
            return True
        
        # safe_api_call関数を使用
        result = safe_api_call(
            client.client,
            model=config.deployment,
            input="テスト質問: 3+3は？",
            reasoning={"effort": "low"}
        )
        
        if hasattr(result, 'output_text'):
            print("OK safe_api_call関数テスト成功")
            print(f"   回答: {result.output_text[:50]}...")
            return True
        else:
            print(f"NG safe_api_call関数テスト失敗: {result}")
            return False
            
    except Exception as e:
        print(f"safe_api_call関数テストエラー: {e}")
        return False


if __name__ == "__main__":
    success1 = test_api_connection()
    success2 = test_safe_api_call()
    
    if success1 and success2:
        print("\n✅ 全てのテストが成功しました！モジュールは正常に動作しています。")
        sys.exit(0)
    else:
        print("\n❌ 一部のテストが失敗しました。")
        sys.exit(1)