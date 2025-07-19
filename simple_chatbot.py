#!/usr/bin/env python3
"""
o3-pro シンプルチャットボット

モード切り替え対応の基本的なチャットボット
- 基本推論（low/medium/high effort）  
- ストリーミング応答
- チャット履歴保存

使用方法:
    python simple_chatbot.py

作成日: 2025-07-19
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.azure_auth import O3ProConfig, O3ProClient
from handlers import ReasoningHandler, StreamingHandler
from chat_history import ChatHistoryManager


class SimpleO3ProChatBot:
    """シンプルo3-proチャットボット"""
    
    def __init__(self):
        self.config = None
        self.client = None
        self.reasoning_handler = None
        self.streaming_handler = None
        self.history_manager = None
        self.current_session_id = None
        self.current_mode = "reasoning"
        self.current_effort = "low"
    
    def initialize(self) -> bool:
        """システム初期化"""
        try:
            print("🚀 o3-proチャットボット初期化中...")
            
            # 設定・認証
            self.config = O3ProConfig()
            if not self.config.validate():
                print("❌ 設定エラー: .envファイルを確認してください")
                return False
            
            self.client = O3ProClient(self.config)
            if not self.client.is_ready():
                print("❌ Azure OpenAI接続失敗")
                return False
            
            print("✅ Azure OpenAI接続成功")
            
            # ハンドラー初期化
            self.reasoning_handler = ReasoningHandler(self.client)
            self.streaming_handler = StreamingHandler(self.client)
            print("✅ 処理ハンドラー初期化完了")
            
            # 履歴管理
            self.history_manager = ChatHistoryManager()
            self.current_session_id = self.history_manager.start_new_session(
                self.current_mode, 
                f"チャットセッション"
            )
            print("✅ 履歴管理初期化完了")
            
            return True
            
        except Exception as e:
            print(f"❌ 初期化エラー: {e}")
            return False
    
    def process_message(self, user_input: str) -> dict:
        """メッセージ処理"""
        try:
            # ユーザーメッセージを履歴に保存
            self.history_manager.add_message(
                self.current_session_id, 
                "user", 
                user_input
            )
            
            # モード別処理
            if self.current_mode == "reasoning":
                result = self.reasoning_handler.basic_reasoning(
                    user_input, 
                    effort=self.current_effort
                )
            elif self.current_mode == "streaming":
                print("💬 ストリーミング応答:")
                
                def stream_callback(chunk_text):
                    print(chunk_text, end='', flush=True)
                
                result = self.streaming_handler.stream_with_callback(
                    user_input,
                    stream_callback,
                    effort=self.current_effort
                )
            else:
                result = {
                    "success": False,
                    "error": f"未対応モード: {self.current_mode}"
                }
            
            # アシスタント応答を履歴に保存
            if result["success"]:
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
            return {
                "success": False,
                "error": f"処理エラー: {e}"
            }
    
    def set_mode(self, mode: str, effort: str = "low") -> bool:
        """モード変更"""
        valid_modes = ["reasoning", "streaming"]
        valid_efforts = ["low", "medium", "high"]
        
        if mode not in valid_modes:
            print(f"❌ 無効なモード: {mode}. 有効: {valid_modes}")
            return False
        
        if effort not in valid_efforts:
            print(f"❌ 無効なeffort: {effort}. 有効: {valid_efforts}")
            return False
        
        self.current_mode = mode
        self.current_effort = effort
        
        print(f"✅ モード変更: {mode} (effort: {effort})")
        return True
    
    def show_help(self):
        """ヘルプ表示"""
        help_text = """
=== o3-proチャットボット コマンド ===

基本:
  /help           - ヘルプ表示
  /quit, /exit    - 終了
  /status         - 現在の設定表示
  
モード切り替え:
  /mode reasoning [effort]  - 基本推論モード (effort: low/medium/high)
  /mode streaming [effort]  - ストリーミングモード
  
セッション:
  /new [タイトル]  - 新セッション開始
  /history        - 履歴表示

使用例:
  /mode reasoning high     - 高精度推論モード
  /new 数学の質問          - 新セッション開始
  こんにちは               - 通常の質問
        """
        print(help_text)
    
    def show_status(self):
        """ステータス表示"""
        print(f"\n=== 現在のステータス ===")
        print(f"モード: {self.current_mode}")
        print(f"Effort: {self.current_effort}")
        print(f"セッションID: {self.current_session_id}")
        
        if self.current_session_id:
            session_info = self.history_manager.get_session_info(self.current_session_id)
            if session_info:
                print(f"メッセージ数: {session_info['message_count']}")
        print()
    
    def show_history(self):
        """履歴表示"""
        if not self.current_session_id:
            print("セッションがありません")
            return
        
        messages = self.history_manager.get_session_messages(self.current_session_id)
        if not messages:
            print("メッセージがありません")
            return
        
        print(f"\n=== セッション履歴 (最新5件) ===")
        for msg in messages[-5:]:  # 最新5件のみ表示
            role = "👤" if msg["role"] == "user" else "🤖"
            content = msg["content"]
            if len(content) > 80:
                content = content[:80] + "..."
            
            timestamp = msg["timestamp"][:19]
            print(f"{role} [{timestamp}] {content}")
        print()
    
    def start_new_session(self, title: str = ""):
        """新セッション開始"""
        if not title:
            title = f"チャットセッション ({self.current_mode})"
        
        self.current_session_id = self.history_manager.start_new_session(
            self.current_mode, 
            title
        )
        print(f"✅ 新セッション開始: {title}")


def main():
    """メイン関数"""
    chatbot = SimpleO3ProChatBot()
    
    if not chatbot.initialize():
        print("初期化に失敗しました")
        return
    
    print("\n💡 /help でコマンド一覧を表示")
    print("💬 チャットを開始してください。終了するには /quit\n")
    
    while True:
        try:
            # プロンプト表示
            mode_indicator = f"[{chatbot.current_mode}/{chatbot.current_effort}]"
            
            try:
                user_input = input(f"{mode_indicator} > ").strip()
            except EOFError:
                print("\n👋 終了します")
                break
            
            if not user_input:
                continue
            
            # コマンド処理
            if user_input.startswith('/'):
                parts = user_input[1:].split()
                command = parts[0].lower()
                
                if command in ['quit', 'exit']:
                    print("👋 終了します")
                    break
                elif command == 'help':
                    chatbot.show_help()
                elif command == 'status':
                    chatbot.show_status()
                elif command == 'history':
                    chatbot.show_history()
                elif command == 'new':
                    title = ' '.join(parts[1:]) if len(parts) > 1 else ""
                    chatbot.start_new_session(title)
                elif command == 'mode':
                    if len(parts) >= 2:
                        mode = parts[1]
                        effort = parts[2] if len(parts) >= 3 else "low"
                        chatbot.set_mode(mode, effort)
                    else:
                        print("使用方法: /mode <reasoning|streaming> [effort]")
                else:
                    print(f"未知のコマンド: {command}. /help で確認してください")
                
                continue
            
            # 通常メッセージ処理
            print()  # 改行
            
            result = chatbot.process_message(user_input)
            
            if result["success"]:
                # ストリーミング以外は結果表示
                if chatbot.current_mode != "streaming":
                    print(f"🤖 {result['response']}")
                
                duration = result.get("duration", 0)
                print(f"\n⏱️  実行時間: {duration:.1f}秒")
            else:
                print(f"❌ エラー: {result['error']}")
            
            print()  # 間隔
            
        except KeyboardInterrupt:
            print("\n\n👋 終了します")
            break
        except Exception as e:
            print(f"\n❌ エラー: {e}")
            continue


if __name__ == "__main__":
    main()