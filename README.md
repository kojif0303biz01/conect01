# o3-pro チャットボットツールキット

## 📋 プロジェクト概要

Azure OpenAI o3-proモデルを使用したモジュール化チャットボットシステムです。既存の動作確認済みコードを活用し、再利用可能なモジュール群を構築しました。

### 🎯 主要機能

- **o3-pro 3つの処理モード完全対応**
  - 基本推論（low/medium/high effort対応）
  - ストリーミング応答（リアルタイム表示）
  - バックグラウンド処理（長時間タスク対応）
- **チャット履歴管理**（JSONベース、将来的にAzure DB対応予定）
- **堅牢な認証機能**（API Key・Azure AD両方対応）
- **高度なエラーハンドリング**（reasoning.summary自動修正など）
- **簡単チャットボット**（コマンドライン対話）

### 🚀 クイックスタート

```bash
# 1. 依存関係インストール
pip install -r requirements.txt

# 2. 環境変数設定（.envファイル作成）
cp .env.example .env
# .envファイルを編集してAzure OpenAI設定を追加

# 3. チャットボット起動
python simple_chatbot.py

# 4. テスト実行（オプション）
python test_modules.py
```

### 🗂️ プロジェクト構造

```
conect01/
├── README.md                     # プロジェクト概要（本ファイル）
├── MODULE_SPECIFICATIONS.md      # モジュール仕様書
├── DESIGN_DOCUMENT.md            # 設計仕様書
├── requirements.txt               # 依存関係
├── .env                          # 環境変数（要設定）
├── .env.example                  # 環境変数例
├── progress_tracker.json         # 開発進捗管理
├── CLAUDE.md                     # Claude Code設定
│
├── core/                         # コアモジュール群
│   ├── __init__.py
│   ├── azure_auth.py            # Azure認証・設定管理
│   ├── error_handler.py         # エラーハンドリング
│   └── chat_history.py          # チャット履歴管理
│
├── handlers/                     # 処理モードハンドラー群
│   ├── __init__.py
│   ├── reasoning_handler.py     # 基本推論処理
│   ├── streaming_handler.py     # ストリーミング処理
│   └── background_handler.py    # バックグラウンド処理
│
├── テストファイル群
│   ├── test_modules.py          # モジュール単体テスト
│   ├── api_connection_test.py   # API接続テスト
│   └── test_chat_history_integration.py  # 履歴統合テスト
│
├── o3_pro_complete_toolkit.py    # 元の統合ツールキット
├── docs/                         # ドキュメント類
└── old/                          # 旧ファイル格納
```

## 🚀 クイックスタート

### 1. 環境準備

```bash
# 仮想環境作成・アクティベート
python3 -m venv venv
source venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt
```

### 2. 環境変数設定

`.env.example`を`.env`にコピーし、Azure OpenAI情報を設定：

```bash
cp .env.example .env
# .envファイルを編集してAzure OpenAI設定を入力
```

必要な環境変数：
```
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=O3-pro
```

### 3. 動作確認

```bash
# モジュールテスト
python test_modules.py

# API接続テスト
python api_connection_test.py

# 履歴管理統合テスト
python test_chat_history_integration.py
```

## 📚 設計仕様

### アーキテクチャ概要

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLIアプリ     │    │  チャットボット  │    │   Webアプリ     │
│                │    │     コア        │    │                │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                │
                    ┌─────────────────┐
                    │   handlers/     │
                    │  処理モード群   │
                    └─────────────────┘
                                │
                    ┌─────────────────┐
                    │     core/       │
                    │  基盤モジュール │
                    └─────────────────┘
                                │
                    ┌─────────────────┐
                    │  Azure OpenAI   │
                    │   o3-pro API   │
                    └─────────────────┘
```

### モジュール設計原則

1. **分離性**: 各モジュールは独立して動作可能
2. **再利用性**: 他のプロジェクトでも利用可能
3. **デバッグ済みコード流用**: 既存の動作確認済み機能を最大限活用
4. **段階的テスト**: 各モジュール個別テスト → 統合テスト

### データフロー

```
User Input → CLI/Chat Interface → Mode Handler → Azure API → Response → History Manager → User Output
                                        ↓
                                 Error Handler (自動エラー修正)
```

## 🔧 開発進捗

### 完了済み（✅）
- [x] 既存コード分析・モジュール設計
- [x] 認証モジュール分離（`core/azure_auth.py`）
- [x] 3つの処理モードハンドラー分離（`handlers/`）
- [x] エラーハンドリング分離（`core/error_handler.py`）
- [x] チャット履歴管理システム（`chat_history/`）
- [x] 全モジュール動作確認・API接続テスト完了
- [x] **シンプルチャットボット実装（`simple_chatbot.py`）**
- [x] **統合テスト・モジュールテスト完了**
- [x] **プロジェクト構造整理・requirements.txt作成**

### 将来拡張予定（📅）
- [ ] Azure Functions対応
- [ ] Cosmos DB履歴管理対応  
- [ ] Web UI実装
- [ ] パッケージ配布対応

## 🧪 テスト結果

### モジュールテスト
- **認証モジュール**: ✅ API Key・Azure AD認証対応
- **エラーハンドリング**: ✅ reasoning.summary自動修正確認
- **ハンドラー群**: ✅ 3モード全て正常動作
- **履歴管理**: ✅ セッション管理・検索機能確認

### API接続テスト
- **基本推論**: ✅ 5.0-5.9秒で正常応答
- **ストリーミング**: ✅ リアルタイムチャンク配信確認
- **エラー処理**: ✅ 自動リトライ・修正機能確認

### 統合テスト
- **履歴+API**: ✅ 3質問で6メッセージ正常保存・検索

## 📖 使用方法

### 1. チャットボットを使用（推奨）

```bash
# チャットボット起動
python simple_chatbot.py

# チャットボット内でのコマンド例
[reasoning/low] > こんにちは
[reasoning/low] > /mode streaming high
[streaming/high] > 複雑な質問を聞かせてください
[streaming/high] > /history
[streaming/high] > /quit
```

### 2. プログラムから直接使用

```python
from core.azure_auth import O3ProConfig, O3ProClient
from handlers import ReasoningHandler
from chat_history import ChatHistoryManager

# 設定・認証
config = O3ProConfig()
client = O3ProClient(config, auth_method="api_key")

# 履歴管理
history = ChatHistoryManager()
session_id = history.start_new_session("reasoning", "テストチャット")

# 推論実行
handler = ReasoningHandler(client)
result = handler.basic_reasoning("2+2は？", effort="low")

# 履歴保存
history.add_message(session_id, "user", "2+2は？")
history.add_message(session_id, "assistant", result["response"], {
    "duration": result["duration"], "mode": "reasoning"
})
```

詳細な使用方法は[MODULE_SPECIFICATIONS.md](MODULE_SPECIFICATIONS.md)を参照してください。

## 🛠️ 開発・運用コマンド

```bash
# 開発環境セットアップ
source venv/bin/activate

# テスト実行
python test_modules.py              # モジュール単体テスト
python api_connection_test.py       # API接続テスト

# コード品質チェック
flake8 core/ handlers/              # リント
mypy core/ handlers/                # 型チェック
black core/ handlers/               # フォーマット

# 元のツールキット実行
python o3_pro_complete_toolkit.py  # 統合ツールキット（参考用）
```

## 📋 要件・依存関係

### システム要件
- Python 3.12+
- Azure OpenAI o3-pro デプロイメント
- API Key または Azure AD認証情報

### 主要依存関係
- `openai>=1.68.0` - Azure OpenAI SDK
- `python-dotenv>=1.0.0` - 環境変数管理
- `azure-identity>=1.15.0` - Azure AD認証

完全な依存関係は[requirements.txt](requirements.txt)を参照。

## 🐛 トラブルシューティング

### よくある問題

1. **認証エラー**
   ```bash
   # .env設定確認
   cat .env
   
   # 認証テスト
   python -c "from core import O3ProConfig; print(O3ProConfig().validate())"
   ```

2. **API接続エラー**
   ```bash
   # 接続テスト実行
   python api_connection_test.py
   ```

3. **モジュールインポートエラー**
   ```bash
   # 仮想環境確認
   which python
   pip list | grep openai
   ```

## 🤝 貢献・開発

### 開発フロー
1. 機能追加前に動作確認テスト実行
2. モジュール単位での段階的開発
3. 各段階で動作確認・テスト実行
4. 進捗を`progress_tracker.json`に記録

### コードスタイル
- 型ヒント使用
- docstring記述
- エラーハンドリング必須
- 既存パターン踏襲

## 📄 ライセンス

本プロジェクトはAzure OpenAI o3-pro検証・開発用です。

## 📞 サポート

問題や質問がある場合は、以下のテストを実行して結果を共有してください：

```bash
python test_modules.py > test_results.log 2>&1
python api_connection_test.py >> test_results.log 2>&1
```

---

**更新日**: 2025-07-19  
**版**: v1.0  
**対応API**: Azure OpenAI 2025-04-01-preview  
**o3-proモデル**: 全機能対応（基本推論・ストリーミング・バックグラウンド）

resoning モード、動作はOKだが、回答が2回表示されている？デバッグ情報がでている？
streamモード、回答が表示されない。