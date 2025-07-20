#!/usr/bin/env python3
"""
履歴管理モジュール統合テスト

実際のAPI呼び出しと履歴管理を組み合わせたテスト

実行方法:
    source venv/bin/activate && python test_chat_history_integration.py

作成日: 2025-07-19
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core import O3ProConfig, O3ProClient, ChatHistoryManager
from handlers import ReasoningHandler


def test_chat_history_with_api():
    """API呼び出しと履歴管理の統合テスト"""
    print("=" * 60)
    print("履歴管理 + API呼び出し 統合テスト開始")
    print("=" * 60)
    
    try:
        # 設定とクライアント初期化
        print("\n=== 初期化 ===")
        config = O3ProConfig()
        if not config.validate():
            print("NG 設定が不正です")
            return False
        
        client = O3ProClient(config, auth_method="api_key")
        if not client.is_ready():
            print("NG クライアント初期化失敗")
            return False
        
        print("OK 設定とクライアント初期化成功")
        
        # 履歴マネージャー初期化
        history_manager = ChatHistoryManager("integration_test_history")
        print("OK 履歴マネージャー初期化成功")
        
        # 推論ハンドラー初期化
        reasoning_handler = ReasoningHandler(client)
        print("OK 推論ハンドラー初期化成功")
        
        # 新しいチャットセッション開始
        print("\n=== チャットセッション開始 ===")
        session_id = history_manager.start_new_session(
            mode="reasoning", 
            title="API統合テストセッション"
        )
        
        if not session_id:
            print("NG セッション作成失敗")
            return False
        
        print(f"OK セッション作成成功: {session_id}")
        
        # 質問と回答のサイクルテスト
        test_questions = [
            "5+3の計算をしてください",
            "日本の首都はどこですか？",
            "簡単な挨拶をしてください"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n=== 質問 {i}: {question} ===")
            
            # ユーザーメッセージを履歴に追加
            if not history_manager.add_message(session_id, "user", question):
                print(f"NG ユーザーメッセージ追加失敗")
                return False
            
            print("OK ユーザーメッセージ履歴追加")
            
            # API呼び出し実行
            result = reasoning_handler.basic_reasoning(question, effort="low")
            
            if not result["success"]:
                print(f"NG API呼び出し失敗: {result.get('error')}")
                return False
            
            print(f"OK API呼び出し成功（{result['duration']:.1f}秒）")
            print(f"   回答: {result['response'][:50]}...")
            
            # アシスタント回答を履歴に追加
            metadata = {
                "mode": "reasoning",
                "effort": "low",
                "duration": result["duration"],
                "api_success": True
            }
            
            if not history_manager.add_message(
                session_id, 
                "assistant", 
                result["response"], 
                metadata
            ):
                print("NG アシスタントメッセージ追加失敗")
                return False
            
            print("OK アシスタントメッセージ履歴追加")
        
        # 履歴検証
        print("\n=== 履歴検証 ===")
        messages = history_manager.get_session_messages(session_id)
        
        if not messages:
            print("NG メッセージ取得失敗")
            return False
        
        expected_count = len(test_questions) * 2  # 質問と回答のペア
        if len(messages) != expected_count:
            print(f"NG メッセージ数不一致: 期待{expected_count}、実際{len(messages)}")
            return False
        
        print(f"OK 履歴検証成功: {len(messages)}メッセージ")
        
        # 履歴表示
        for i, msg in enumerate(messages, 1):
            role = msg["role"]
            content = msg["content"][:30] + "..." if len(msg["content"]) > 30 else msg["content"]
            timestamp = msg["timestamp"][:19]  # 秒まで表示
            
            print(f"   {i}. [{timestamp}] {role}: {content}")
            
            if role == "assistant" and "metadata" in msg:
                metadata = msg["metadata"]
                if "duration" in metadata:
                    print(f"      → API実行時間: {metadata['duration']:.1f}秒")
        
        # 検索機能テスト
        print("\n=== 検索機能テスト ===")
        search_results = history_manager.search_messages("計算", session_id)
        
        if search_results:
            print(f"OK 検索成功: 「計算」で{len(search_results)}件")
            for result in search_results:
                print(f"   [{result['role']}] {result['content'][:40]}...")
        else:
            print("INFO 検索結果なし（正常）")
        
        # セッション情報確認
        print("\n=== セッション情報確認 ===")
        session_info = history_manager.get_session_info(session_id)
        
        if session_info:
            print("OK セッション情報取得成功")
            print(f"   タイトル: {session_info['title']}")
            print(f"   モード: {session_info['mode']}")
            print(f"   メッセージ数: {session_info['message_count']}")
            print(f"   作成日時: {session_info['created_at'][:19]}")
        else:
            print("NG セッション情報取得失敗")
            return False
        
        # 統計情報確認
        print("\n=== 統計情報確認 ===")
        stats = history_manager.get_statistics()
        
        if stats:
            print("OK 統計情報取得成功")
            print(f"   総セッション数: {stats['total_sessions']}")
            print(f"   総メッセージ数: {stats['total_messages']}")
            print(f"   モード別統計: {stats['mode_statistics']}")
        else:
            print("NG 統計情報取得失敗")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 履歴管理 + API呼び出し 統合テスト成功！")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\nERROR 統合テスト中にエラー: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # テストディレクトリクリーンアップ
        try:
            import shutil
            test_path = Path("integration_test_history")
            if test_path.exists():
                shutil.rmtree(test_path)
                print(f"テストディレクトリ削除: integration_test_history")
        except Exception as e:
            print(f"クリーンアップエラー: {e}")


if __name__ == "__main__":
    success = test_chat_history_with_api()
    sys.exit(0 if success else 1)