"""
Azure OpenAI o3-pro 完全版ツールキット

このモジュールは、Azure OpenAI o3-proモデルのすべての機能を
統合した包括的なツールキットです。

機能:
- API Key / Azure AD 両方の認証対応
- 推論レベル別テスト（low/medium/high）
- ストリーミング応答
- エラーハンドリング
- 設定管理
- デバッグ機能

使用方法:
python o3_pro_complete_toolkit.py

作成日: 2025-01-19
対応API: 2025-04-01-preview
"""

import os
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv


class O3ProConfig:
    """o3-pro設定管理クラス"""
    
    def __init__(self, env_path: Optional[str] = None):
        """設定を初期化"""
        if env_path:
            load_dotenv(env_path, override=True)
        else:
            load_dotenv(override=True)
        
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "O3-pro")
        self.api_version = "2025-04-01-preview"
        self.client_id = os.getenv("AZURE_CLIENT_ID")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET")
        self.tenant_id = os.getenv("AZURE_TENANT_ID")
    
    def validate(self) -> bool:
        """設定の妥当性をチェック"""
        if not self.endpoint:
            print("NG AZURE_OPENAI_ENDPOINT が設定されていません")
            return False
        
        if not self.api_key and not self.has_azure_ad_config():
            print("NG API Key または Azure AD 設定が必要です")
            return False
        
        return True
    
    def has_azure_ad_config(self) -> bool:
        """Azure AD設定があるかチェック"""
        return bool(self.client_id and self.client_secret and self.tenant_id)
    
    def print_config(self):
        """設定情報を表示（機密情報は伏せる）"""
        print("=== 設定情報 ===")
        print(f"エンドポイント: {self.endpoint}")
        print(f"デプロイメント: {self.deployment}")
        print(f"API バージョン: {self.api_version}")
        print(f"API Key: {'設定済み' if self.api_key else '未設定'}")
        print(f"Azure AD: {'設定済み' if self.has_azure_ad_config() else '未設定'}")


class O3ProClient:
    """o3-pro専用クライアントクラス"""
    
    def __init__(self, config: O3ProConfig, auth_method: str = "auto"):
        """
        クライアント初期化
        
        Args:
            config: 設定オブジェクト
            auth_method: 認証方法 ("api_key", "azure_ad", "auto")
        """
        self.config = config
        self.client = None
        self.auth_method = auth_method
        self._initialize_client()
    
    def _initialize_client(self):
        """クライアントを初期化"""
        try:
            from openai import AzureOpenAI
            
            if self.auth_method == "api_key" or (
                self.auth_method == "auto" and self.config.api_key
            ):
                print("API Key認証でクライアント初期化中...")
                self.client = AzureOpenAI(
                    api_key=self.config.api_key,
                    azure_endpoint=self.config.endpoint,
                    api_version=self.config.api_version
                )
                print("OK API Key認証成功")
                
            elif self.auth_method == "azure_ad" or (
                self.auth_method == "auto" and self.config.has_azure_ad_config()
            ):
                print("Azure AD認証でクライアント初期化中...")
                from azure.identity import DefaultAzureCredential, get_bearer_token_provider
                
                token_provider = get_bearer_token_provider(
                    DefaultAzureCredential(),
                    "https://cognitiveservices.azure.com/.default"
                )
                
                self.client = AzureOpenAI(
                    azure_endpoint=self.config.endpoint,
                    azure_ad_token_provider=token_provider,
                    api_version=self.config.api_version
                )
                print("OK Azure AD認証成功")
                
            else:
                raise ValueError("有効な認証方法が設定されていません")
                
        except Exception as e:
            print(f"NG クライアント初期化失敗: {e}")
            self.client = None
    
    def is_ready(self) -> bool:
        """クライアントが使用可能かチェック"""
        return self.client is not None
    
    def test_connection(self) -> bool:
        """接続テスト"""
        if not self.is_ready():
            return False
        
        try:
            print("接続テスト中...")
            models = self.client.models.list()
            print(f"OK 接続成功（モデル数: {len(models.data)}）")
            return True
        except Exception as e:
            print(f"NG 接続失敗: {e}")
            return False


class O3ProTester:
    """o3-pro機能テストクラス"""
    
    def __init__(self, client: O3ProClient):
        """テスター初期化"""
        self.client = client
        self.deployment = client.config.deployment
    
    def test_basic_reasoning(self) -> bool:
        """基本推論テスト"""
        print("\n=== 基本推論テスト ===")
        
        try:
            response = self.client.client.responses.create(
                model=self.deployment,
                input="1+1=?",
                reasoning={"effort": "low"}
            )
            
            result = response.output_text
            print(f"質問: 1+1=?")
            print(f"回答: {result}")
            print("OK 基本推論成功")
            return True
            
        except Exception as e:
            print(f"NG 基本推論失敗: {e}")
            return False
    
    def test_reasoning_levels(self) -> Dict[str, Any]:
        """推論レベル別テスト"""
        print("\n=== 推論レベル別テスト ===")
        
        question = "97は素数ですか？理由も教えてください。"
        levels = ["low", "medium", "high"]
        results = {}
        
        for level in levels:
            try:
                print(f"\n{level.upper()}レベルテスト中...")
                start_time = time.time()
                
                response = self.client.client.responses.create(
                    model=self.deployment,
                    input=question,
                    reasoning={"effort": level}
                )
                
                duration = time.time() - start_time
                result_text = response.output_text
                
                results[level] = {
                    "success": True,
                    "response": result_text,
                    "duration": duration
                }
                
                print(f"OK {level.upper()}レベル成功（{duration:.1f}秒）")
                print(f"回答: {result_text[:100]}...")
                
            except Exception as e:
                print(f"NG {level.upper()}レベル失敗: {e}")
                results[level] = {
                    "success": False,
                    "error": str(e),
                    "duration": 0
                }
        
        return results
    
    def test_streaming(self) -> bool:
        """ストリーミングテスト"""
        print("\n=== ストリーミングテスト ===")
        
        try:
            print("ストリーミング開始...")
            
            stream = self.client.client.responses.create(
                model=self.deployment,
                input="日本の首都について簡潔に教えてください",
                reasoning={"effort": "low"},
                stream=True
            )
            
            full_response = ""
            chunk_count = 0
            
            for chunk in stream:
                chunk_count += 1
                if hasattr(chunk, 'output_text'):
                    print(chunk.output_text, end='', flush=True)
                    full_response += chunk.output_text
            
            print()  # 改行
            print(f"OK ストリーミング成功（チャンク数: {chunk_count}）")
            return True
            
        except Exception as e:
            print(f"NG ストリーミング失敗: {e}")
            return False
    
    def test_error_scenarios(self) -> Dict[str, Any]:
        """エラーシナリオテスト"""
        print("\n=== エラーシナリオテスト ===")
        
        scenarios = {
            "invalid_effort": {
                "params": {
                    "model": self.deployment,
                    "input": "テスト",
                    "reasoning": {"effort": "invalid"}
                },
                "expect_error": True
            },
            "empty_input": {
                "params": {
                    "model": self.deployment,
                    "input": "",
                    "reasoning": {"effort": "low"}
                },
                "expect_error": True
            }
        }
        
        results = {}
        
        for scenario_name, scenario_data in scenarios.items():
            try:
                print(f"\n{scenario_name}テスト中...")
                
                response = self.client.client.responses.create(
                    **scenario_data["params"]
                )
                
                if scenario_data["expect_error"]:
                    print(f"WARN {scenario_name}: エラーが期待されましたが成功しました")
                    results[scenario_name] = {
                        "success": True,
                        "unexpected": True,
                        "response": response.output_text
                    }
                else:
                    print(f"OK {scenario_name}: 正常に成功")
                    results[scenario_name] = {
                        "success": True,
                        "response": response.output_text
                    }
                    
            except Exception as e:
                if scenario_data["expect_error"]:
                    print(f"OK {scenario_name}: 期待通りエラー発生")
                    results[scenario_name] = {
                        "success": True,
                        "expected_error": True,
                        "error": str(e)
                    }
                else:
                    print(f"NG {scenario_name}: 予期しないエラー")
                    results[scenario_name] = {
                        "success": False,
                        "error": str(e)
                    }
        
        return results


def create_safe_response(client, **kwargs) -> Optional[Any]:
    """
    安全なAPI呼び出し関数
    一般的なエラーを自動修正してリトライ
    """
    try:
        return client.responses.create(**kwargs)
    except Exception as e:
        error_str = str(e)
        
        # reasoning.summary エラーの自動修正
        if "reasoning.summary" in error_str:
            print("reasoning.summaryエラーを検出、encrypted_contentに変更してリトライ...")
            kwargs['include'] = ["reasoning.encrypted_content"]
            kwargs['store'] = False
            return client.responses.create(**kwargs)
        
        # その他のエラーは再発生
        raise e


def print_summary(test_results: Dict[str, Any]):
    """テスト結果サマリーを表示"""
    print("\n" + "="*50)
    print("テスト結果サマリー")
    print("="*50)
    
    total_tests = 0
    passed_tests = 0
    
    for test_name, result in test_results.items():
        print(f"\n{test_name}:")
        
        if isinstance(result, dict):
            if "levels" in result:  # 推論レベルテストの場合
                for level, level_result in result["levels"].items():
                    total_tests += 1
                    status = "OK" if level_result.get("success") else "NG"
                    print(f"  {level}: {status}")
                    if level_result.get("success"):
                        passed_tests += 1
            else:
                total_tests += 1
                status = "OK" if result.get("success") else "NG"
                print(f"  結果: {status}")
                if result.get("success"):
                    passed_tests += 1
        else:
            total_tests += 1
            status = "OK" if result else "NG"
            print(f"  結果: {status}")
            if result:
                passed_tests += 1
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"\n成功率: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate == 100:
        print("SUCCESS すべてのテストが成功しました！")
    elif success_rate >= 80:
        print("OK ほとんどのテストが成功しました")
    else:
        print("WARNING 失敗したテストがあります")


def main():
    """メイン実行関数"""
    print("Azure OpenAI o3-pro 完全版ツールキット")
    print("="*50)
    
    # 設定初期化
    env_path = Path(__file__).parent / ".env"
    config = O3ProConfig(str(env_path))
    config.print_config()
    
    if not config.validate():
        print("\nERROR 設定が不正です。.envファイルを確認してください")
        return
    
    # 認証方法選択
    print("\n認証方法を選択してください:")
    print("1. API Key認証（推奨）")
    print("2. Azure AD認証")
    print("3. 自動選択")
    
    choice = input("選択 (1-3, Enter=3): ").strip() or "3"
    
    auth_methods = {
        "1": "api_key",
        "2": "azure_ad", 
        "3": "auto"
    }
    
    auth_method = auth_methods.get(choice, "auto")
    
    # クライアント初期化
    client = O3ProClient(config, auth_method)
    
    if not client.is_ready():
        print("\nERROR クライアント初期化に失敗しました")
        return
    
    # 接続テスト
    if not client.test_connection():
        print("\nERROR 接続テストに失敗しました")
        return
    
    # テスト実行
    tester = O3ProTester(client)
    test_results = {}
    
    print("\nテストを開始します...")
    
    # 基本推論テスト
    test_results["basic_reasoning"] = tester.test_basic_reasoning()
    
    # 推論レベル別テスト
    test_results["reasoning_levels"] = {
        "levels": tester.test_reasoning_levels()
    }
    
    # ストリーミングテスト
    test_results["streaming"] = tester.test_streaming()
    
    # エラーシナリオテスト
    test_results["error_scenarios"] = tester.test_error_scenarios()
    
    # 結果サマリー表示
    print_summary(test_results)
    
    # 結果をJSONファイルに保存
    result_file = Path(__file__).parent / "test_results.json"
    try:
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False, default=str)
        print(f"\nテスト結果を保存しました: {result_file}")
    except Exception as e:
        print(f"結果保存エラー: {e}")


if __name__ == "__main__":
    main()