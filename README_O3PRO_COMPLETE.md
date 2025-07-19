# Azure OpenAI o3-pro モデル 完全セットアップガイド

## 概要

このドキュメントは、Azure OpenAI o3-proモデル（推論モデル）を使用するための完全なセットアップガイドです。API Key認証とAzure AD認証の両方の方法、よくある問題と解決方法、動作確認済みのプログラムコードを提供します。

## 📋 プロジェクト構成

```
conect01/
├── README_O3PRO_COMPLETE.md          # このドキュメント
├── o3_pro_complete_toolkit.py        # 完全版ツールキット
├── o3_pro_simple_demo.py             # 動作確認済み簡単デモ
├── requirements.txt                  # 依存関係
├── .env                              # 環境変数設定
├── azure_cli_setup.py               # Azure CLI認証セットアップ
├── debug_azure_cli.py               # Azure CLI デバッグツール
└── direct_azure_test.py             # Azure認証直接テスト
```

## 🚀 クイックスタート

### 1. 環境セットアップ

```bash
# 仮想環境作成
python -m venv venv
venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt
```

### 2. 環境変数設定

`.env` ファイルを作成：

```env
# Azure OpenAI 設定（必須）
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2025-04-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=O3-pro

# Azure AD認証用（オプション - CLI認証時は不要）
# AZURE_CLIENT_ID=your-client-id
# AZURE_CLIENT_SECRET=your-client-secret
# AZURE_TENANT_ID=your-tenant-id
```

### 3. 動作確認

```bash
# 簡単デモ実行
python o3_pro_simple_demo.py

# 完全版ツールキット実行
python o3_pro_complete_toolkit.py
```

## 🔑 認証方法

### 方法1: API Key認証（推奨・最も簡単）

```python
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2025-04-01-preview"
)
```

### 方法2: Azure AD/Microsoft Entra ID認証

```python
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI

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

## 🧠 o3-proモデル使用方法

### 基本的な使用方法

```python
# シンプルな推論
response = client.responses.create(
    model="O3-pro",  # デプロイメント名（大文字のO）
    input="1+1=?",
    reasoning={"effort": "low"}  # low/medium/high
)

print(response.output_text)
```

### 推論レベル別の使い分け

| レベル | 用途 | 特徴 |
|--------|------|------|
| `low` | 簡単な質問、基本計算 | 高速、低コスト |
| `medium` | 一般的な問題解決 | バランス型 |
| `high` | 複雑な推論、研究課題 | 高精度、時間とコスト高 |

## 📊 実装済み機能

### ✅ 動作確認済み機能

1. **基本推論**（全レベル対応）
2. **ストリーミング応答**
3. **背景処理**
4. **エラーハンドリング**
5. **環境変数管理**

### ⚠️ 制限事項

1. **encrypted_content使用時**: `store=False`が必須
2. **max_completion_tokens**: Responses APIでは未対応
3. **reasoning.summary**: 利用不可（代替: encrypted_content）

## 🛠️ トラブルシューティング

### よくあるエラーと解決方法

#### 1. 文字化けエラー
```
UnicodeDecodeError: 'cp932' codec can't decode
```
**解決**: 特殊文字（✓✗🎉）を英語（OK/NG/SUCCESS）に変更

#### 2. reasoning.summary無効エラー
```
Invalid value for 'include': reasoning.summary
```
**解決**: `reasoning.encrypted_content`を使用し、`store=False`を追加

#### 3. Azure CLI認識エラー
```
'az' は、内部コマンドまたは外部コマンドとして認識されません
```
**解決**: PowerShellを再起動、またはPATHを手動更新

### デバッグスクリプト

```bash
# Azure CLI問題の診断
python debug_azure_cli.py

# Azure認証の直接テスト
python direct_azure_test.py

# Azure CLI セットアップ
python azure_cli_setup.py
```

## 📝 コード例

### 完全版の使用例

```python
# o3_pro_complete_toolkit.py から抜粋

def test_reasoning_levels(client):
    """推論レベル別テスト"""
    levels = ["low", "medium", "high"]
    question = "素数判定: 97は素数ですか？"
    
    for level in levels:
        try:
            response = client.responses.create(
                model="O3-pro",
                input=question,
                reasoning={"effort": level}
            )
            print(f"{level.upper()}: {response.output_text}")
        except Exception as e:
            print(f"{level.upper()} エラー: {e}")

def stream_response(client):
    """ストリーミング応答の例"""
    stream = client.responses.create(
        model="O3-pro",
        input="日本の首都について教えてください",
        reasoning={"effort": "medium"},
        stream=True
    )
    
    for chunk in stream:
        if hasattr(chunk, 'output_text'):
            print(chunk.output_text, end='')
```

## 🔧 設定ファイル詳細

### requirements.txt
```txt
openai>=1.68.0
azure-identity>=1.19.0
azure-ai-inference>=1.0.0b9
python-dotenv>=1.0.0
```

### .env設定例
```env
# 必須設定
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2025-04-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=O3-pro

# Azure AD認証用（オプション） 現時点未確認
# AZURE_CLIENT_ID=your-client-id
# AZURE_CLIENT_SECRET=your-client-secret  
# AZURE_TENANT_ID=your-tenant-id
```

## 🎯 ベストプラクティス

### 1. エラーハンドリング

```python
def safe_api_call(client, **kwargs):
    """安全なAPI呼び出し"""
    try:
        return client.responses.create(**kwargs)
    except Exception as e:
        error_msg = str(e)
        if "reasoning.summary" in error_msg:
            # encrypted_contentに変更してリトライ
            kwargs['include'] = ["reasoning.encrypted_content"] 
            kwargs['store'] = False
            return client.responses.create(**kwargs)
        raise e
```

### 2. 設定管理

```python
class O3ProConfig:
    """o3-pro設定管理クラス"""
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") 
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "O3-pro")
        self.api_version = "2025-04-01-preview"
    
    def validate(self):
        """設定の妥当性チェック"""
        required = ["api_key", "endpoint"]
        missing = [k for k in required if not getattr(self, k)]
        if missing:
            raise ValueError(f"必要な設定が不足: {missing}")
```

### 3. レスポンス処理

```python
def extract_response_data(response):
    """レスポンスからデータを安全に抽出"""
    result = {
        "output": response.output_text,
        "model": getattr(response, 'model', 'unknown'),
        "usage": None
    }
    
    # 使用量情報の安全な抽出
    if hasattr(response, 'usage'):
        try:
            result["usage"] = {
                "reasoning_tokens": response.usage.reasoning_tokens,
                "total_tokens": response.usage.total_tokens
            }
        except:
            result["usage"] = str(response.usage)
    
    return result
```

## 🔍 Azure認証の現状と対策

### 現在の状況
- ✅ API Key認証: 完全に動作
- ⚠️ Azure CLI認証: PATH問題で認識されない
- ❌ CLIENT_ID認証: 設定方法要確認

### 解決策

#### 1. Azure CLI PATH問題の解決
```powershell
# PowerShell で実行
$env:PATH += ';C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin'
az --version
```

#### 2. 新しいPowerShellセッション（推奨）
```bash
# 現在のPowerShellを閉じて新しく開く
# 仮想環境を再有効化
venv\Scripts\activate
az --version
python azure_cli_setup.py
```

## 📋 チェックリスト

開発開始前の確認事項：

- [ ] Python 3.8+ インストール済み
- [ ] 仮想環境作成・有効化
- [ ] requirements.txtからパッケージインストール
- [ ] .envファイル作成・設定
- [ ] Azure OpenAIリソース作成済み
- [ ] o3-proモデルデプロイ済み（名前: "O3-pro"）
- [ ] API Key取得済み
- [ ] 基本動作確認（o3_pro_simple_demo.py）

## 🚨 重要な注意点

1. **デプロイメント名**: "O3-pro"（大文字のO）
2. **API Version**: "2025-04-01-preview" 必須
3. **encrypted_content**: store=False必須
4. **文字エンコーディング**: UTF-8特殊文字に注意
5. **ストリーミング**: 部分的対応、実装に注意

## 📞 サポート

問題が発生した場合：

1. `debug_azure_cli.py`でAzure CLI状況確認
2. `direct_azure_test.py`で認証テスト
3. エラーメッセージの詳細を確認
4. このドキュメントのトラブルシューティング参照

---

**更新日**: 2025-01-19  
**対応モデル**: Azure OpenAI o3-pro  
**API Version**: 2025-04-01-preview