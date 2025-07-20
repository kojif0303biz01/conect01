#!/usr/bin/env python3
"""
o3-pro チャットボットコア

モード切り替え対応チャットボットシステム
- 基本推論（low/medium/high effort）
- ストリーミング応答
- バックグラウンド処理

作成日: 2025-07-19
"""

import sys
import time
from pathlib import Path
from typing import Dict, Optional, Any

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core import O3ProConfig, O3ProClient, ChatHistoryManager
from handlers import ReasoningHandler, StreamingHandler, BackgroundHandler


class O3ProChatBot:
    """o3-pro チャットボットメインクラス"""
    
    def __init__(self, auth_method: str = "api_key"):
        """
        チャットボット初期化
        
        Args:
            auth_method: 認証方法 ("api_key" | "azure_ad" | "auto")
        """
        self.config = None
        self.client = None
        self.history_manager = None
        self.current_session_id = None
        self.current_mode = "reasoning"
        self.current_effort = "low"
        
        # ハンドラー
        self.reasoning_handler = None
        self.streaming_handler = None
        self.background_handler = None
        
        # 初期化
        self.auth_method = auth_method
        self.initialize()
    
    def initialize(self) -> bool:
        """システム初期化"""
        try:
            print("=== o3-pro チャットボット初期化 ===")
            
            # 設定・認証
            self.config = O3ProConfig()
            if not self.config.validate():
                print("ERROR: 設定が不正です。.envファイルを確認してください。")
                return False
            
            self.client = O3ProClient(self.config, auth_method=self.auth_method)
            if not self.client.is_ready():
                print("ERROR: Azure OpenAI接続に失敗しました。")
                return False
            
            print("✓ Azure OpenAI接続成功")
            
            # 履歴管理
            self.history_manager = ChatHistoryManager()
            print("✓ 履歴管理システム初期化")
            
            # ハンドラー初期化
            self.reasoning_handler = ReasoningHandler(self.client)
            self.streaming_handler = StreamingHandler(self.client)
            self.background_handler = BackgroundHandler(self.client)
            print("✓ 処理ハンドラー初期化完了")
            
            print("🚀 チャットボット準備完了\n")
            return True
            
        except Exception as e:
            print(f"ERROR: 初期化エラー: {e}")
            return False
    
    def start_new_session(self, title: str = "") -> bool:
        """新しいチャットセッション開始"""
        try:
            if not title:
                title = f"チャットセッション ({time.strftime('%Y-%m-%d %H:%M')})"
            
            self.current_session_id = self.history_manager.start_new_session(
                mode=self.current_mode,
                title=title
            )
            
            if self.current_session_id:
                print(f"✓ 新セッション開始: {title}")
                print(f"  セッションID: {self.current_session_id}")
                return True
            else:
                print("ERROR: セッション作成に失敗しました")
                return False
                
        except Exception as e:
            print(f"ERROR: セッション開始エラー: {e}")
            return False
    
    def set_mode(self, mode: str, effort: str = "low") -> bool:
        """処理モード変更"""
        valid_modes = ["reasoning", "streaming", "background"]
        valid_efforts = ["low", "medium", "high"]
        
        if mode not in valid_modes:
            print(f"ERROR: 無効なモード: {mode}. 有効: {valid_modes}")
            return False
        
        if effort not in valid_efforts:
            print(f"ERROR: 無効なeffortレベル: {effort}. 有効: {valid_efforts}")
            return False
        
        self.current_mode = mode
        self.current_effort = effort
        
        print(f"✓ モード変更: {mode} (effort: {effort})")
        return True
    
    def process_message(self, user_input: str) -> Dict[str, Any]:
        """メッセージ処理メイン"""
        try:
            # ユーザーメッセージを履歴に追加
            if self.current_session_id:
                self.history_manager.add_message(
                    self.current_session_id, 
                    "user", 
                    user_input
                )
            
            # モード別処理
            if self.current_mode == "reasoning":
                result = self._process_reasoning(user_input)
            elif self.current_mode == "streaming":
                result = self._process_streaming(user_input)
            elif self.current_mode == "background":
                result = self._process_background(user_input)
            else:
                result = {
                    "success": False,
                    "error": f"未対応モード: {self.current_mode}"
                }
            
            # アシスタント回答を履歴に追加
            if result["success"] and self.current_session_id:
                metadata = {
                    "mode": self.current_mode,
                    "effort": self.current_effort,
                    "duration": result.get("duration", 0)
                }
                
                self.history_manager.add_message(
                    self.current_session_id,
                    "assistant",
                    result["response"],
                    metadata
                )
            
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"メッセージ処理エラー: {e}"
            }
            return error_result
    
    def _process_reasoning(self, user_input: str) -> Dict[str, Any]:
        """基本推論処理"""
        return self.reasoning_handler.basic_reasoning(
            user_input, 
            effort=self.current_effort
        )
    
    def _process_streaming(self, user_input: str) -> Dict[str, Any]:
        """ストリーミング処理"""
        print("💬 ストリーミング応答:")
        
        # コールバック関数でリアルタイム表示
        def stream_callback(chunk_text):
            print(chunk_text, end='', flush=True)
        
        return self.streaming_handler.stream_with_callback(
            user_input,
            stream_callback,
            effort=self.current_effort
        )
    
    def _process_background(self, user_input: str) -> Dict[str, Any]:
        """バックグラウンド処理"""
        print("⏳ バックグラウンド処理開始...")
        
        # タスク開始
        start_result = self.background_handler.start_background_task(
            user_input,
            effort=self.current_effort
        )
        
        if not start_result["success"]:
            return start_result
        
        job_id = start_result["job_id"]
        print(f"   ジョブID: {job_id}")
        
        # 完了待機（簡易ポーリング）
        max_wait = 300  # 5分
        polling_interval = 10  # 10秒間隔
        elapsed = 0
        
        while elapsed < max_wait:
            status_result = self.background_handler.check_status(job_id)
            
            if not status_result["success"]:
                return status_result
            
            status = status_result["status"]
            print(f"   ステータス: {status} ({elapsed}秒経過)")
            
            if status == "completed":
                final_result = self.background_handler.get_result(job_id)
                print("✅ バックグラウンド処理完了")
                return final_result
            elif status == "failed":
                return {
                    "success": False,
                    "error": "バックグラウンド処理が失敗しました"
                }
            
            time.sleep(polling_interval)
            elapsed += polling_interval
        
        return {
            "success": False,
            "error": f"タイムアウト: {max_wait}秒以内に完了しませんでした"
        }
    
    def show_help(self):
        """ヘルプ表示"""
        help_text = """
=== o3-pro チャットボット コマンド ===

基本コマンド:
  /help           - このヘルプを表示
  /quit, /exit    - チャットボット終了
  /clear          - 画面クリア
  
モード切り替え:
  /mode reasoning [effort]  - 基本推論モード (effort: low/medium/high)
  /mode streaming [effort]  - ストリーミングモード
  /mode background [effort] - バックグラウンド処理モード
  
セッション管理:
  /new [タイトル]  - 新しいセッション開始
  /sessions       - セッション一覧表示
  /history        - 現在のセッション履歴表示
  
情報表示:
  /status         - 現在の設定状況表示
  /stats          - 履歴統計表示

使用例:
  /mode reasoning high     - 高精度推論モードに変更
  /new 数学の質問          - 新セッション「数学の質問」開始
  こんにちは               - 通常の質問・会話
        """
        print(help_text)
    
    def show_status(self):
        """現在のステータス表示"""
        print(f"\n=== 現在のステータス ===")
        print(f"モード: {self.current_mode}")
        print(f"Effortレベル: {self.current_effort}")
        print(f"セッションID: {self.current_session_id or '未開始'}")
        
        if self.current_session_id:
            session_info = self.history_manager.get_session_info(self.current_session_id)
            if session_info:
                print(f"セッション名: {session_info['title']}")
                print(f"メッセージ数: {session_info['message_count']}")
        print()
    
    def show_sessions(self):
        """セッション一覧表示"""
        sessions = self.history_manager.list_sessions(limit=10)
        
        if not sessions:
            print("セッションがありません。")
            return
        
        print(f"\n=== 最新セッション一覧 (最大10件) ===")
        for i, session in enumerate(sessions, 1):
            session_id = session.get('id', 'Unknown')
            title = session.get('title', 'タイトルなし')
            mode = session.get('mode', 'Unknown')
            message_count = session.get('message_count', 0)
            created_at = session.get('created_at', '')[:19]
            
            current_mark = " ← 現在" if session_id == self.current_session_id else ""
            print(f"{i:2d}. [{session_id[:8]}] {title}")
            print(f"     {mode}モード | {message_count}メッセージ | {created_at}{current_mark}")
        print()
    
    def show_history(self):
        """現在のセッション履歴表示"""
        if not self.current_session_id:
            print("アクティブなセッションがありません。")
            return
        
        messages = self.history_manager.get_session_messages(self.current_session_id)
        if not messages:
            print("メッセージがありません。")
            return
        
        print(f"\n=== セッション履歴 ===")
        for i, msg in enumerate(messages, 1):
            role = msg["role"]
            content = msg["content"]
            timestamp = msg["timestamp"][:19]
            
            # ロール表示
            role_symbol = "👤" if role == "user" else "🤖"
            print(f"{i:2d}. {role_symbol} [{timestamp}] {role}:")
            
            # 内容表示（長い場合は短縮）
            if len(content) > 100:
                print(f"     {content[:100]}...")
            else:
                print(f"     {content}")
            
            # メタデータ表示
            if role == "assistant" and "metadata" in msg:
                metadata = msg["metadata"]
                if "duration" in metadata:
                    print(f"     (実行時間: {metadata['duration']:.1f}秒)")
            print()
    
    def show_statistics(self):
        """統計情報表示"""
        stats = self.history_manager.get_statistics()
        
        if not stats:
            print("統計情報がありません。")
            return
        
        print(f"\n=== 履歴統計 ===")
        print(f"総セッション数: {stats['total_sessions']}")
        print(f"総メッセージ数: {stats['total_messages']}")
        
        if 'mode_statistics' in stats:
            print("\nモード別統計:")
            for mode, count in stats['mode_statistics'].items():
                print(f"  {mode}: {count}セッション")
        print()


def main():
    """メイン関数"""
    try:
        # チャットボット初期化
        chatbot = O3ProChatBot()
        
        if not chatbot.initialize():
            print("チャットボットの初期化に失敗しました。")
            return
        
        # 初期セッション開始
        chatbot.start_new_session("初回セッション")
        
        # ヘルプ表示
        print("💡 /help でコマンド一覧を表示できます。")
        print("💬 チャットを開始してください。終了するには /quit と入力してください。\n")
        
        # メインループ
        while True:
            try:
                # プロンプト表示
                mode_indicator = f"[{chatbot.current_mode}/{chatbot.current_effort}]"
                user_input = input(f"{mode_indicator} > ").strip()
                
                if not user_input:
                    continue
                
                # コマンド処理
                if user_input.startswith('/'):
                    command_parts = user_input[1:].split()
                    command = command_parts[0].lower()
                    
                    if command in ['quit', 'exit']:
                        print("👋 チャットボットを終了します。")
                        break
                    elif command == 'help':
                        chatbot.show_help()
                    elif command == 'clear':
                        import os
                        os.system('clear' if os.name == 'posix' else 'cls')
                    elif command == 'status':
                        chatbot.show_status()
                    elif command == 'sessions':
                        chatbot.show_sessions()
                    elif command == 'history':
                        chatbot.show_history()
                    elif command == 'stats':
                        chatbot.show_statistics()
                    elif command == 'new':
                        title = ' '.join(command_parts[1:]) if len(command_parts) > 1 else ""
                        chatbot.start_new_session(title)
                    elif command == 'mode':
                        if len(command_parts) >= 2:
                            mode = command_parts[1]
                            effort = command_parts[2] if len(command_parts) >= 3 else "low"
                            chatbot.set_mode(mode, effort)
                        else:
                            print("使用方法: /mode <reasoning|streaming|background> [effort]")
                    else:
                        print(f"未知のコマンド: {command}. /help で使用可能なコマンドを確認してください。")
                    
                    continue
                
                # 通常メッセージ処理
                print()  # 改行で読みやすく
                
                start_time = time.time()
                result = chatbot.process_message(user_input)
                
                if result["success"]:
                    # ストリーミング以外は結果表示
                    if chatbot.current_mode != "streaming":
                        print(f"🤖 {result['response']}")
                    
                    duration = result.get("duration", time.time() - start_time)
                    print(f"\n⏱️  実行時間: {duration:.1f}秒")
                else:
                    print(f"❌ エラー: {result['error']}")
                
                print()  # 次の入力との間隔
                
            except KeyboardInterrupt:
                print("\n\n👋 チャットボットを終了します。")
                break
            except Exception as e:
                print(f"\n❌ 予期しないエラー: {e}")
                continue
    
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()