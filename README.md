# Azure OpenAI o3-pro ライブラリ & チャットボット

Azure OpenAI o3-proモデル用の汎用ライブラリとチャットボットアプリケーション

## 🚀 プロジェクト概要

このプロジェクトは2つの主要コンポーネントで構成されています：

### 1. 汎用ライブラリモジュール（core & handlers）
他のプロジェクトでも再利用可能な、Azure認証とo3-pro API操作のライブラリ群

### 2. チャットボットアプリケーション（simple_chatbot.py）
上記ライブラリを使用した実装例としてのチャットボットアプリ

## 📦 プロジェクト構造

```
conect01/
├── core/                        # 汎用コアライブラリ
│   ├── azure_universal_auth.py  # Azure汎用認証基盤
│   ├── azure_auth.py           # Azure OpenAI認証・接続
│   ├── error_handler.py        # エラーハンドリング
│   └── README.md               # ライブラリ使用ガイド
├── handlers/                    # o3-pro処理ハンドラー
│   ├── reasoning_handler.py     # 推論モード
│   ├── streaming_handler.py     # ストリーミングモード
│   ├── background_handler.py    # バックグラウンドモード
│   └── README.md               # ハンドラー使用ガイド
├── chat_history/               # チャット履歴管理
│   └── local_history.py        # ローカル履歴管理
├── simple_chatbot.py           # サンプルチャットボットアプリ
├── tests/                      # テストスクリプト
│   ├── test_azure_universal_auth.py    # 認証基盤テスト
│   └── test_azure_auth_integration.py  # 統合テスト
├── docs/                       # ドキュメント
└── old/                        # 旧実装（参考用）
```

## 🎯 主な機能

### ライブラリ機能
- **Azure汎用認証**: az login、Service Principal、Managed Identity対応
- **o3-pro API操作**: 推論、ストリーミング、バックグラウンド処理
- **エラーハンドリング**: リトライ機能付き統一エラー処理

### チャットボット機能
- **3つの処理モード**: 
  - 基本推論（low/medium/high effort）
  - ストリーミング応答
  - バックグラウンド処理
- **チャット履歴管理**: JSONベースのローカル履歴保存
- **ジョブ管理**: バックグラウンドジョブの追跡・管理

## 🚀 クイックスタート

### 1. ライブラリとして使用

```python
# Azure認証
from core.azure_universal_auth import quick_auth, get_azure_token
token = get_azure_token("cognitive_services")

# o3-pro API操作
from core.azure_auth import O3ProConfig, O3ProClient
from handlers import ReasoningHandler

config = O3ProConfig()
client = O3ProClient(config)
handler = ReasoningHandler(client)

result = handler.basic_reasoning("質問内容", effort="low")
```

### 2. チャットボットアプリとして使用

```bash
# 環境準備
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 環境変数設定
cp .env.example .env
# .envファイルを編集

# チャットボット起動
python simple_chatbot.py
```

## 📚 ドキュメント

### ライブラリ仕様書
- [Azure汎用認証基盤](core/azure_universal_auth_spec.md)
- [Azure OpenAI認証](core/azure_auth_spec.md)
- [エラーハンドラー](core/error_handler_spec.md)
- [推論ハンドラー](handlers/reasoning_handler_spec.md)
- [ストリーミングハンドラー](handlers/streaming_handler_spec.md)
- [バックグラウンドハンドラー](handlers/background_handler_spec.md)

### 使用ガイド
- [Coreライブラリ使用ガイド](core/README.md)
- [Handlersライブラリ使用ガイド](handlers/README.md)

## 🔧 環境設定

### 必須環境変数（.env）

```bash
# Azure OpenAI設定
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=O3-pro

# Azure AD認証（オプション）
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
```

### 認証方式

1. **APIキー認証**（デフォルト）
2. **Azure CLI認証**（`az login`）
3. **Service Principal認証**
4. **Managed Identity認証**（Azure環境）

## 🧪 テスト

```bash
# 認証基盤テスト
python tests/test_azure_universal_auth.py

# o3-pro統合テスト
python tests/test_azure_auth_integration.py
```

## 📋 要件

- Python 3.12+
- Azure OpenAI o3-proデプロイメント
- APIキーまたはAzure AD認証

### 依存関係
```
openai>=1.5.0
azure-identity>=1.15.0
python-dotenv>=1.0.0
```

## 🛠️ 開発状況

### ✅ 完了済み
- Azure汎用認証基盤（8つのAzureサービス対応）
- o3-pro全モード対応（推論・ストリーミング・バックグラウンド）
- エラーハンドリング・リトライ機能
- チャット履歴管理
- サンプルチャットボット

### 🔍 動作確認済み
- Azure CLI認証でのo3-pro接続
- 全3モードでの推論実行
- トークン取得（Cognitive Services, Storage, Key Vault）
- エラーハンドリングとフォールバック

### 📅 今後の拡張予定
- Service Principal認証の実運用テスト
- 他のAzureサービスでの実装例
- Azure Functions対応
- Web UI実装

## 📄 ライセンス

内部使用のみ。再配布時は要相談。

## 📞 サポート

問題がある場合は、以下のテストを実行して結果を共有してください：

```bash
python tests/test_azure_universal_auth.py > test_results.log 2>&1
python tests/test_azure_auth_integration.py >> test_results.log 2>&1
```

---

**更新日**: 2025-07-20  
**バージョン**: v2.0  
**対応API**: Azure OpenAI 2025-04-01-preview