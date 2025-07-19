"""
チャット履歴管理モジュール

既存のo3_pro_complete_toolkit.pyから抽出したJSONファイル処理パターンを基に
チャット履歴の保存・読み込み・検索機能を提供

使用方法:
    from core.chat_history import ChatHistoryManager
    
    # 履歴マネージャー初期化
    history_manager = ChatHistoryManager("chat_sessions")
    
    # 新しいセッション開始
    session_id = history_manager.start_new_session("基本推論モード")
    
    # メッセージ記録
    history_manager.add_message(session_id, "user", "2+2は？")
    history_manager.add_message(session_id, "assistant", "2+2=4です", {
        "mode": "reasoning", "effort": "low", "duration": 3.2
    })
    
    # 履歴取得
    messages = history_manager.get_session_messages(session_id)

作成日: 2025-07-19（o3_pro_complete_toolkit.pyのJSONパターンから抽出）
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import uuid


class ChatHistoryManager:
    """チャット履歴管理クラス（動作確認済みJSONパターン使用）"""
    
    def __init__(self, history_dir: str = "chat_history"):
        """
        履歴マネージャー初期化
        
        Args:
            history_dir: 履歴ファイル保存ディレクトリ
        """
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(exist_ok=True)
        
        # インデックスファイル（セッション一覧管理）
        self.index_file = self.history_dir / "sessions_index.json"
        self.ensure_index_file()
    
    def ensure_index_file(self):
        """インデックスファイルの存在確認と初期化"""
        if not self.index_file.exists():
            initial_index = {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_sessions": 0,
                "sessions": {}
            }
            self.save_json_file(self.index_file, initial_index)
    
    def save_json_file(self, file_path: Path, data: Dict[str, Any]) -> bool:
        """
        JSONファイル保存（既存パターン流用）
        
        Args:
            file_path: 保存先ファイルパス
            data: 保存するデータ
            
        Returns:
            保存成功フラグ
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            print(f"JSON保存失敗 {file_path}: {e}")
            return False
    
    def load_json_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        JSONファイル読み込み（既存パターン流用）
        
        Args:
            file_path: 読み込みファイルパス
            
        Returns:
            読み込んだデータまたはNone
        """
        try:
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"JSON読み込み失敗 {file_path}: {e}")
            return None
    
    def start_new_session(self, mode: str = "general", title: str = "") -> str:
        """
        新しいチャットセッションを開始
        
        Args:
            mode: チャットモード ("reasoning", "streaming", "background", "general")
            title: セッションタイトル（省略時は自動生成）
            
        Returns:
            セッションID
        """
        session_id = str(uuid.uuid4())[:8]  # 短縮UUID
        current_time = datetime.now()
        
        if not title:
            title = f"{mode}チャット_{current_time.strftime('%m%d_%H%M')}"
        
        # セッションデータ作成
        session_data = {
            "session_id": session_id,
            "title": title,
            "mode": mode,
            "created_at": current_time.isoformat(),
            "last_updated": current_time.isoformat(),
            "message_count": 0,
            "messages": []
        }
        
        # セッションファイル保存
        session_file = self.history_dir / f"session_{session_id}.json"
        if not self.save_json_file(session_file, session_data):
            return None
        
        # インデックス更新
        index_data = self.load_json_file(self.index_file)
        if index_data:
            index_data["sessions"][session_id] = {
                "title": title,
                "mode": mode,
                "created_at": current_time.isoformat(),
                "last_updated": current_time.isoformat(),
                "message_count": 0,
                "file_path": f"session_{session_id}.json"
            }
            index_data["total_sessions"] = len(index_data["sessions"])
            index_data["last_updated"] = current_time.isoformat()
            
            self.save_json_file(self.index_file, index_data)
        
        print(f"新しいセッション開始: {session_id} ({title})")
        return session_id
    
    def add_message(
        self, 
        session_id: str, 
        role: str, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        セッションにメッセージを追加
        
        Args:
            session_id: セッションID
            role: 送信者ロール ("user", "assistant", "system")
            content: メッセージ内容
            metadata: 追加メタデータ（処理時間、モードなど）
            
        Returns:
            追加成功フラグ
        """
        session_file = self.history_dir / f"session_{session_id}.json"
        session_data = self.load_json_file(session_file)
        
        if not session_data:
            print(f"セッション {session_id} が見つかりません")
            return False
        
        current_time = datetime.now()
        message = {
            "timestamp": current_time.isoformat(),
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        
        # メッセージ追加
        session_data["messages"].append(message)
        session_data["message_count"] = len(session_data["messages"])
        session_data["last_updated"] = current_time.isoformat()
        
        # セッションファイル更新
        if not self.save_json_file(session_file, session_data):
            return False
        
        # インデックス更新
        self.update_session_index(session_id, session_data["message_count"], current_time.isoformat())
        
        return True
    
    def update_session_index(self, session_id: str, message_count: int, last_updated: str):
        """セッションインデックスを更新"""
        index_data = self.load_json_file(self.index_file)
        if index_data and session_id in index_data["sessions"]:
            index_data["sessions"][session_id]["message_count"] = message_count
            index_data["sessions"][session_id]["last_updated"] = last_updated
            index_data["last_updated"] = last_updated
            self.save_json_file(self.index_file, index_data)
    
    def get_session_messages(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        セッションのメッセージ一覧を取得
        
        Args:
            session_id: セッションID
            
        Returns:
            メッセージリストまたはNone
        """
        session_file = self.history_dir / f"session_{session_id}.json"
        session_data = self.load_json_file(session_file)
        
        if session_data:
            return session_data.get("messages", [])
        return None
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """セッション情報を取得"""
        session_file = self.history_dir / f"session_{session_id}.json"
        session_data = self.load_json_file(session_file)
        
        if session_data:
            return {
                "session_id": session_data["session_id"],
                "title": session_data["title"],
                "mode": session_data["mode"],
                "created_at": session_data["created_at"],
                "last_updated": session_data["last_updated"],
                "message_count": session_data["message_count"]
            }
        return None
    
    def list_sessions(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        セッション一覧を取得
        
        Args:
            limit: 取得件数制限
            
        Returns:
            セッション情報リスト（最新順）
        """
        index_data = self.load_json_file(self.index_file)
        if not index_data:
            return []
        
        sessions = list(index_data["sessions"].values())
        
        # 最新順にソート
        sessions.sort(key=lambda x: x["last_updated"], reverse=True)
        
        if limit:
            sessions = sessions[:limit]
        
        return sessions
    
    def search_messages(self, query: str, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        メッセージ検索
        
        Args:
            query: 検索クエリ
            session_id: 特定セッション内検索（省略時は全セッション対象）
            
        Returns:
            検索結果リスト
        """
        results = []
        
        if session_id:
            # 特定セッション内検索
            sessions_to_search = [session_id]
        else:
            # 全セッション検索
            index_data = self.load_json_file(self.index_file)
            if not index_data:
                return results
            sessions_to_search = list(index_data["sessions"].keys())
        
        for sid in sessions_to_search:
            messages = self.get_session_messages(sid)
            if not messages:
                continue
            
            session_info = self.get_session_info(sid)
            
            for msg in messages:
                if query.lower() in msg["content"].lower():
                    result = {
                        "session_id": sid,
                        "session_title": session_info["title"] if session_info else "不明",
                        "timestamp": msg["timestamp"],
                        "role": msg["role"],
                        "content": msg["content"],
                        "metadata": msg.get("metadata", {})
                    }
                    results.append(result)
        
        # 時系列順にソート
        results.sort(key=lambda x: x["timestamp"], reverse=True)
        return results
    
    def delete_session(self, session_id: str) -> bool:
        """
        セッションを削除
        
        Args:
            session_id: 削除するセッションID
            
        Returns:
            削除成功フラグ
        """
        session_file = self.history_dir / f"session_{session_id}.json"
        
        # セッションファイル削除
        try:
            if session_file.exists():
                session_file.unlink()
        except Exception as e:
            print(f"セッションファイル削除失敗: {e}")
            return False
        
        # インデックスから削除
        index_data = self.load_json_file(self.index_file)
        if index_data and session_id in index_data["sessions"]:
            del index_data["sessions"][session_id]
            index_data["total_sessions"] = len(index_data["sessions"])
            index_data["last_updated"] = datetime.now().isoformat()
            self.save_json_file(self.index_file, index_data)
        
        print(f"セッション {session_id} を削除しました")
        return True
    
    def export_session(self, session_id: str, export_path: Optional[str] = None) -> Optional[str]:
        """
        セッションをエクスポート
        
        Args:
            session_id: エクスポートするセッションID
            export_path: エクスポート先パス（省略時は自動生成）
            
        Returns:
            エクスポートファイルパスまたはNone
        """
        session_data = self.load_json_file(self.history_dir / f"session_{session_id}.json")
        if not session_data:
            return None
        
        if not export_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = f"chat_export_{session_id}_{timestamp}.json"
        
        export_file = Path(export_path)
        if self.save_json_file(export_file, session_data):
            print(f"セッションエクスポート完了: {export_path}")
            return str(export_file)
        
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """履歴統計情報を取得"""
        index_data = self.load_json_file(self.index_file)
        if not index_data:
            return {}
        
        total_messages = sum(s.get("message_count", 0) for s in index_data["sessions"].values())
        
        # モード別集計
        mode_stats = {}
        for session in index_data["sessions"].values():
            mode = session.get("mode", "unknown")
            if mode not in mode_stats:
                mode_stats[mode] = {"sessions": 0, "messages": 0}
            mode_stats[mode]["sessions"] += 1
            mode_stats[mode]["messages"] += session.get("message_count", 0)
        
        return {
            "total_sessions": index_data["total_sessions"],
            "total_messages": total_messages,
            "created_at": index_data["created_at"],
            "last_updated": index_data["last_updated"],
            "mode_statistics": mode_stats
        }


# テスト関数
def test_chat_history_manager():
    """チャット履歴マネージャーのテスト"""
    print("チャット履歴マネージャーテスト開始...")
    
    # テスト用ディレクトリ
    test_dir = "test_chat_history"
    manager = ChatHistoryManager(test_dir)
    
    try:
        # 新しいセッション作成
        print("\n=== セッション作成テスト ===")
        session_id = manager.start_new_session("reasoning", "テストセッション")
        if session_id:
            print(f"OK セッション作成成功: {session_id}")
        else:
            print("NG セッション作成失敗")
            return False
        
        # メッセージ追加テスト
        print("\n=== メッセージ追加テスト ===")
        if manager.add_message(session_id, "user", "テスト質問: 2+2は？"):
            print("OK ユーザーメッセージ追加成功")
        else:
            print("NG ユーザーメッセージ追加失敗")
            return False
        
        metadata = {"mode": "reasoning", "effort": "low", "duration": 3.2}
        if manager.add_message(session_id, "assistant", "2+2=4です", metadata):
            print("OK アシスタントメッセージ追加成功")
        else:
            print("NG アシスタントメッセージ追加失敗")
            return False
        
        # メッセージ取得テスト
        print("\n=== メッセージ取得テスト ===")
        messages = manager.get_session_messages(session_id)
        if messages and len(messages) == 2:
            print(f"OK メッセージ取得成功: {len(messages)}件")
            for i, msg in enumerate(messages, 1):
                print(f"   {i}. [{msg['role']}] {msg['content'][:30]}...")
        else:
            print("NG メッセージ取得失敗")
            return False
        
        # セッション一覧テスト
        print("\n=== セッション一覧テスト ===")
        sessions = manager.list_sessions()
        if sessions:
            print(f"OK セッション一覧取得成功: {len(sessions)}件")
            for session in sessions:
                # list_sessions()は sessions_index.jsonから取得するため、session_idキーは存在しない
                title = session.get('title', '不明')
                message_count = session.get('message_count', 0)
                print(f"   {title} ({message_count}メッセージ)")
        else:
            print("NG セッション一覧取得失敗")
            return False
        
        # 検索テスト
        print("\n=== 検索テスト ===")
        results = manager.search_messages("2+2")
        if results:
            print(f"OK 検索成功: {len(results)}件")
            for result in results:
                print(f"   [{result['role']}] {result['content'][:30]}...")
        else:
            print("NG 検索失敗")
            return False
        
        # 統計情報テスト
        print("\n=== 統計情報テスト ===")
        stats = manager.get_statistics()
        if stats:
            print("OK 統計情報取得成功")
            print(f"   総セッション数: {stats['total_sessions']}")
            print(f"   総メッセージ数: {stats['total_messages']}")
            print(f"   モード別統計: {stats['mode_statistics']}")
        else:
            print("NG 統計情報取得失敗")
            return False
        
        print("\nOK チャット履歴マネージャーテスト成功")
        return True
        
    except Exception as e:
        print(f"ERROR テスト中にエラー: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # テストディレクトリクリーンアップ
        import shutil
        test_path = Path(test_dir)
        if test_path.exists():
            shutil.rmtree(test_path)
            print(f"テストディレクトリ削除: {test_dir}")


if __name__ == "__main__":
    test_chat_history_manager()