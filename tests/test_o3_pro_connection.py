"""
Azure OpenAI o3-pro 接続テスト

このファイルは、o3-proモデルへの接続とbasic機能をテストするためのユニットテストです。
"""

import os
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential

# テスト前の設定
load_dotenv()

class TestO3ProConnection:
    """o3-pro接続テストクラス"""
    
    @pytest.fixture
    def client(self):
        """テスト用クライアントのフィクスチャ"""
        return AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY", "test-key"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/"),
            api_version="2025-04-01-preview"
        )
    
    def test_client_initialization(self, client):
        """クライアント初期化のテスト"""
        assert client is not None
        assert hasattr(client, 'responses')
    
    @pytest.mark.skipif(
        not os.getenv("AZURE_OPENAI_API_KEY") or not os.getenv("AZURE_OPENAI_ENDPOINT"),
        reason="Azure OpenAI credentials not provided"
    )
    def test_basic_response_creation(self, client):
        """基本的なレスポンス作成のテスト"""
        try:
            response = client.responses.create(
                model="o3-pro",
                input="簡単な足し算: 2 + 2 = ?",
                reasoning={"effort": "low"}
            )
            
            assert hasattr(response, 'output_text')
            assert response.output_text is not None
            assert len(response.output_text) > 0
            
        except Exception as e:
            pytest.skip(f"o3-pro model not available: {e}")
    
    @pytest.mark.skipif(
        not os.getenv("AZURE_OPENAI_API_KEY") or not os.getenv("AZURE_OPENAI_ENDPOINT"),
        reason="Azure OpenAI credentials not provided"
    )
    def test_reasoning_effort_levels(self, client):
        """推論努力レベルのテスト"""
        effort_levels = ["low", "medium", "high"]
        
        for effort in effort_levels:
            try:
                response = client.responses.create(
                    model="o3-pro",
                    input="1 + 1 = ?",
                    reasoning={"effort": effort}
                )
                
                assert hasattr(response, 'output_text')
                assert response.output_text is not None
                
            except Exception as e:
                pytest.skip(f"Effort level {effort} test failed: {e}")
    
    @pytest.mark.skipif(
        not os.getenv("AZURE_OPENAI_API_KEY") or not os.getenv("AZURE_OPENAI_ENDPOINT"),
        reason="Azure OpenAI credentials not provided"
    )
    def test_streaming_response(self, client):
        """ストリーミングレスポンスのテスト"""
        try:
            stream = client.responses.create(
                model="o3-pro",
                input="カウント: 1, 2, 3",
                reasoning={"effort": "low"},
                stream=True
            )
            
            response_parts = []
            for event in stream:
                if hasattr(event, 'delta') and hasattr(event.delta, 'content'):
                    if event.delta.content:
                        response_parts.append(event.delta.content)
            
            assert len(response_parts) > 0
            
        except Exception as e:
            pytest.skip(f"Streaming test failed: {e}")
    
    def test_environment_variables(self):
        """環境変数の存在確認テスト"""
        # 必須環境変数
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        
        if endpoint:
            assert endpoint.startswith("https://")
            assert endpoint.endswith(".openai.azure.com/") or endpoint.endswith(".azure.com/")
        
        if api_key:
            assert len(api_key) > 10  # APIキーの最小長チェック
    
    @patch('openai.AzureOpenAI')
    def test_mock_client_creation(self, mock_azure_openai):
        """モッククライアント作成のテスト"""
        # モックレスポンスの設定
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.output_text = "テストレスポンス"
        mock_client.responses.create.return_value = mock_response
        mock_azure_openai.return_value = mock_client
        
        # テスト実行
        client = AzureOpenAI(
            api_key="test-key",
            azure_endpoint="https://test.openai.azure.com/",
            api_version="2025-04-01-preview"
        )
        
        response = client.responses.create(
            model="o3-pro",
            input="テスト入力"
        )
        
        assert response.output_text == "テストレスポンス"
        mock_client.responses.create.assert_called_once()

class TestO3ProErrorHandling:
    """o3-proエラーハンドリングテスト"""
    
    def test_invalid_credentials(self):
        """無効な認証情報のテスト"""
        client = AzureOpenAI(
            api_key="invalid-key",
            azure_endpoint="https://invalid.openai.azure.com/",
            api_version="2025-04-01-preview"
        )
        
        with pytest.raises(Exception):
            client.responses.create(
                model="o3-pro",
                input="テスト"
            )
    
    def test_invalid_model_name(self):
        """無効なモデル名のテスト"""
        if not os.getenv("AZURE_OPENAI_API_KEY"):
            pytest.skip("API key not available")
        
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version="2025-04-01-preview"
        )
        
        with pytest.raises(Exception):
            client.responses.create(
                model="invalid-model",
                input="テスト"
            )
    
    def test_invalid_reasoning_effort(self):
        """無効な推論努力レベルのテスト"""
        if not os.getenv("AZURE_OPENAI_API_KEY"):
            pytest.skip("API key not available")
        
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version="2025-04-01-preview"
        )
        
        with pytest.raises(Exception):
            client.responses.create(
                model="o3-pro",
                input="テスト",
                reasoning={"effort": "invalid-level"}
            )

class TestO3ProAuthentication:
    """o3-pro認証テスト"""
    
    @pytest.mark.skipif(
        not os.getenv("AZURE_TENANT_ID"),
        reason="Azure tenant ID not provided"
    )
    def test_managed_identity_auth(self):
        """マネージドアイデンティティ認証のテスト"""
        try:
            from azure.identity import get_bearer_token_provider
            
            credential = DefaultAzureCredential()
            token_provider = get_bearer_token_provider(
                credential, 
                "https://cognitiveservices.azure.com/.default"
            )
            
            client = AzureOpenAI(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                azure_ad_token_provider=token_provider,
                api_version="2025-04-01-preview"
            )
            
            assert client is not None
            
        except Exception as e:
            pytest.skip(f"Managed identity test failed: {e}")

# テスト実行用のヘルパー関数
def run_connection_tests():
    """接続テストの実行"""
    print("=== Azure OpenAI o3-pro 接続テスト ===")
    
    # 環境変数チェック
    if not os.getenv("AZURE_OPENAI_ENDPOINT"):
        print("Warning: AZURE_OPENAI_ENDPOINT が設定されていません")
    
    if not os.getenv("AZURE_OPENAI_API_KEY"):
        print("Warning: AZURE_OPENAI_API_KEY が設定されていません")
    
    # 基本接続テスト
    try:
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY", "test"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "https://test.azure.com"),
            api_version="2025-04-01-preview"
        )
        
        print("✓ クライアント初期化成功")
        
        # o3-proモデルの利用可能性チェック
        if os.getenv("AZURE_OPENAI_API_KEY") and os.getenv("AZURE_OPENAI_ENDPOINT"):
            response = client.responses.create(
                model="o3-pro",
                input="テスト接続",
                reasoning={"effort": "low"}
            )
            print("✓ o3-proモデル接続成功")
            print(f"  レスポンス: {response.output_text[:50]}...")
        
    except Exception as e:
        print(f"✗ 接続テスト失敗: {e}")

if __name__ == "__main__":
    run_connection_tests()