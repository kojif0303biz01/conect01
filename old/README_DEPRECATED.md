# 非推奨ファイル (Deprecated Files)

⚠️ **重要**: このディレクトリ内のファイルは非推奨です。本番環境では使用しないでください。

## 📅 移行履歴

### 2025-07-20: プロジェクト大規模リファクタリング

以下のファイルが新しいモジュール構造に移行されました：

## 🔄 移行済みファイル

### 1. o3_pro_complete_toolkit.py → 分割
**移行先**:
- `core/azure_auth.py` - Azure OpenAI認証
- `handlers/reasoning_handler.py` - 推論処理
- `handlers/streaming_handler.py` - ストリーミング処理
- `handlers/background_handler.py` - バックグラウンド処理

### 2. 認証関連
- `azure_auth_troubleshoot.py` → `core/azure_auth.py` (統合)
- `check_azure_auth.py` → `core/azure_auth.py` (統合)
- `debug_azure_cli.py` → `core/azure_universal_auth.py` (統合)

### 3. テスト関連
- `api_connection_test.py` → `cosmos_history/tests/` (移行)
- `simple_o3_test.py` → `simple_chatbot.py` (統合)
- `test_*.py` → `cosmos_history/tests/` (移行・統合)

### 4. チャットボット関連
- `chatbot_core.py` → `simple_chatbot.py` (統合)
- `quick_test_o3.py` → `simple_chatbot.py` (統合)

## 🏗️ 新しいアーキテクチャ

### モジュール構造 (2025-07-20)
```
├── core/                    # コアライブラリ
│   ├── azure_auth.py       # Azure OpenAI認証
│   └── azure_universal_auth.py # 汎用Azure認証
├── handlers/               # 処理ハンドラー
│   ├── reasoning_handler.py
│   ├── streaming_handler.py
│   └── background_handler.py
├── cosmos_history/         # Cosmos DB履歴管理
│   ├── models/
│   ├── tests/
│   └── ...
├── simple_chatbot.py      # メインチャットボット
└── cosmos_search.py       # 履歴検索ツール
```

## 📋 機能比較

| 機能 | 旧版 (old/) | 新版 (2025-07-20) |
|------|-------------|-------------------|
| **Azure認証** | 複数ファイル分散 | ✅ `core/azure_auth.py` 統合 |
| **o3-pro処理** | 単一巨大ファイル | ✅ ハンドラー分割 |
| **履歴管理** | ローカルのみ | ✅ Cosmos DB + ローカル |
| **エラー処理** | 個別実装 | ✅ `core/error_handler.py` 統合 |
| **テスト** | 部分的 | ✅ 包括的テストスイート |
| **設定管理** | 散在 | ✅ `cosmos_history/config.py` 統合 |

## 🚫 使用禁止理由

### 1. セキュリティ
- 古い認証方式
- 不十分なエラーハンドリング

### 2. 保守性
- 巨大な単一ファイル
- 機能が密結合

### 3. 機能性
- Cosmos DB対応なし
- TTL設定なし
- 検索機能なし

## 🔍 参考用途のみ

以下の目的でのみ参照可能：

1. **歴史的経緯の理解**
2. **移行前後の比較**
3. **実装アイデアの参考**

## ⚠️ 重要な注意事項

- **本番環境で実行しない**
- **新規開発の基盤にしない**
- **セキュリティ目的で使用しない**

## 🎯 推奨アクション

新しい機能を実装する場合：

1. `simple_chatbot.py` をベースとする
2. `core/` モジュールを活用する
3. `cosmos_history/` で履歴管理
4. `cosmos_search.py` で検索機能

---

**新しいアーキテクチャを使用してください。このディレクトリのファイルは削除検討対象です。**