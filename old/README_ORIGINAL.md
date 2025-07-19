# Azure OpenAI o3-pro 機能テストプロジェクト

このプロジェクトは、Azure OpenAIの最新推論モデル「o3-pro」の機能を包括的にテストするためのサンプルコードとツール群です。

## 📋 プロジェクト概要

- **目的**: Azure OpenAI o3-proモデルの各種機能の検証と使用方法の実演
- **対象**: 最新のResponses API（2025-04-01-preview）を使用
- **特徴**: 基本機能からバックグラウンド処理まで幅広くカバー

## 🚀 主要機能

### o3-proモデルの特徴
- **最高レベルの推論能力**: 複雑な問題解決、数学的証明、科学的分析
- **マルチモーダル対応**: テキスト＋画像入力
- **推論努力レベル制御**: low, medium, high の3段階
- **バックグラウンド処理**: 長時間タスクの非同期実行
- **ストリーミング対応**: リアルタイムでの回答生成

## 📁 プロジェクト構造

```
conect01/
├── src/                    # メインソースコード
│   └── o3_pro_tester.py   # 包括的機能テストプログラム
├── examples/              # 使用例とサンプルコード
│   ├── basic_o3_pro_usage.py        # 基本的な使用例
│   └── advanced_o3_pro_features.py  # 高度な機能デモ
├── tests/                 # テストコード
│   └── test_o3_pro_connection.py   # 接続・基本機能テスト
├── docs/                  # ドキュメント
│   ├── azure_llm_methods_comprehensive.md
│   └── azure_v1_api_o3_pro_guide.md
├── .env.example          # 環境変数テンプレート
├── requirements.txt      # Python依存関係
└── README.md            # このファイル
```

## ⚙️ セットアップ

### 1. リポジトリのクローン
```bash
git clone <repository-url>
cd conect01
```

### 2. 仮想環境の作成と有効化
```bash
# 仮想環境作成
python -m venv venv

# 有効化 (Windows)
venv\Scripts\activate

# 有効化 (Linux/Mac)
source venv/bin/activate
```

### 3. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定
`.env.example`を`.env`にコピーして、必要な値を設定してください：

```bash
cp .env.example .env
```

`.env`ファイルに以下を設定：

```env
# Azure OpenAI設定（必須）
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2025-04-01-preview

# Azure Entra ID認証（オプション）
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret

# o3-proモデルのデプロイメント名
AZURE_OPENAI_DEPLOYMENT_NAME=o3-pro
```

## 🔧 使用方法

### 基本的な使用例
```bash
python examples/basic_o3_pro_usage.py
```

### 包括的機能テスト
```bash
python src/o3_pro_tester.py
```

### 高度な機能デモ
```bash
python examples/advanced_o3_pro_features.py
```

### 接続テスト
```bash
python tests/test_o3_pro_connection.py
```

### Pytestでのテスト実行
```bash
pytest tests/ -v
```

## 💡 コード例

### 基本的な推論
```python
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key="your-api-key",
    azure_endpoint="your-endpoint",
    api_version="2025-04-01-preview"
)

response = client.responses.create(
    model="o3-pro",
    input="複雑な数学問題を解いてください",
    reasoning={"effort": "high"}
)

print(response.output_text)
```

### ストリーミングレスポンス
```python
stream = client.responses.create(
    model="o3-pro",
    input="ステップバイステップで説明してください",
    reasoning={"effort": "medium"},
    stream=True
)

for event in stream:
    if hasattr(event, 'delta') and event.delta.content:
        print(event.delta.content, end="", flush=True)
```

### バックグラウンド処理
```python
response = client.responses.create(
    model="o3-pro",
    input="複雑な研究タスク",
    background=True,
    reasoning={"effort": "high"}
)

# ステータス確認
status = client.responses.retrieve(response.id)
```

## 🧪 テスト内容

### 基本機能テスト
- ✅ クライアント初期化
- ✅ 基本的な推論タスク
- ✅ 推論努力レベル（low/medium/high）
- ✅ エラーハンドリング

### 高度機能テスト
- ✅ マルチモーダル入力（テキスト + 画像）
- ✅ 複雑な問題解決
- ✅ ストリーミングレスポンス
- ✅ バックグラウンド処理
- ✅ 科学的推論
- ✅ 数学的証明
- ✅ アルゴリズム設計
- ✅ コード生成

## 📊 結果出力

テスト実行後、以下の形式で結果が出力されます：

```json
{
  "test_suite": "Azure OpenAI o3-pro Comprehensive Test",
  "timestamp": "2025-01-XX XX:XX:XX",
  "api_version": "2025-04-01-preview",
  "tests": [...],
  "summary": {
    "total_tests": 10,
    "successful_tests": 9,
    "failed_tests": 1,
    "success_rate": "90.0%"
  }
}
```

## 🔒 認証方式

### 1. APIキー認証（簡単）
```python
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2025-04-01-preview"
)
```

### 2. Microsoft Entra ID認証（推奨）
```python
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), 
    "https://cognitiveservices.azure.com/.default"
)

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_ad_token_provider=token_provider,
    api_version="2025-04-01-preview"
)
```

## ⚠️ 注意事項

### o3-proモデルの制限
- **利用制限**: 限定アクセス（要申請）
- **APIアクセス**: Responses API専用（Chat Completions APIは未対応）
- **処理時間**: 高精度推論のため応答時間が長い
- **コスト**: 入力$20/1M、出力$80/1Mトークン

### サポートされていない機能
- `temperature`、`top_p`などのサンプリングパラメータ
- `Canvas`、一時チャット機能
- 画像生成（`max_tokens`の代わりに`max_completion_tokens`を使用）

## 🔄 アップデート情報

- **2025年6月**: o3-pro GA版リリース
- **2025年5月**: v1 API開始予定
- **現在**: プレビュー版で利用可能

## 🐛 トラブルシューティング

### よくある問題

1. **認証エラー**
   ```
   解決策: API キーまたはエンドポイントを確認
   ```

2. **モデル未デプロイエラー**
   ```
   解決策: Azure AI Studio でo3-proモデルをデプロイ
   ```

3. **クォータ制限**
   ```
   解決策: TPM (Token Per Minute) 制限を確認・調整
   ```

4. **タイムアウト**
   ```
   解決策: background=True でバックグラウンド処理を使用
   ```

### デバッグ手順
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 接続テスト
try:
    models = client.models.list()
    print("利用可能なモデル:", [model.id for model in models])
except Exception as e:
    print(f"接続エラー: {e}")
```

## 📚 参考リンク

- [Azure OpenAI 公式ドキュメント](https://learn.microsoft.com/azure/ai-services/openai/)
- [o3-proモデル詳細](https://azure.microsoft.com/blog/o3-and-o4-mini-unlock-enterprise-agent-workflows/)
- [Responses API ガイド](https://learn.microsoft.com/azure/ai-foundry/openai/concepts/models)

## 🤝 貢献

プロジェクトへの貢献を歓迎します！

1. フォークしてブランチを作成
2. 変更を加えてコミット
3. プルリクエストを作成

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 📞 サポート

問題や質問がある場合は、Issueを作成してください。

---

**注意**: o3-proは最新の推論モデルです。利用には事前申請が必要な場合があります。詳細はAzure AI Foundryでご確認ください。