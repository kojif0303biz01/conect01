"""
Azure OpenAI o3-pro機能テストプログラム

このプログラムは、Azure OpenAIのo3-proモデルの各種機能をテストします。
新しいResponses APIを使用し、o3-proの高度な推論機能を検証します。
"""

import os
import asyncio
import time
from typing import Optional, Dict, Any, List
from pathlib import Path
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import logging

# .envファイルの明示的な読み込み
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path, override=True)

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class O3ProTester:
    """o3-proモデルの機能テストクラス"""
    
    def __init__(self, use_managed_identity: bool = False):
        """
        初期化
        
        Args:
            use_managed_identity: Microsoft Entra ID認証を使用するかどうか
        """
        load_dotenv()
        self.use_managed_identity = use_managed_identity
        self.client = self._create_client()
        
    def _create_client(self) -> AzureOpenAI:
        """Azure OpenAIクライアントを作成"""
        if self.use_managed_identity:
            # Microsoft Entra ID認証
            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(), 
                "https://cognitiveservices.azure.com/.default"
            )
            
            client = AzureOpenAI(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                azure_ad_token_provider=token_provider,
                api_version="2025-04-01-preview"  # 最新プレビュー版
            )
        else:
            # APIキー認証
            client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_version="2025-04-01-preview"
            )
        
        logger.info("Azure OpenAI client initialized")
        return client
    
    def test_basic_reasoning(self) -> Dict[str, Any]:
        """基本的な推論能力をテスト"""
        logger.info("Testing basic reasoning capabilities...")
        
        try:
            response = self.client.responses.create(
                model="o3-pro",
                input="次の数学問題を解いてください：x^2 + 5x + 6 = 0",
                reasoning={"effort": "medium"},  # 推論努力レベル
                include=["reasoning.encrypted_content"],    # 推論プロセス表示
                store=False  # 永続化無効（encrypted_content使用時に必須）
            )
            
            return {
                "test_name": "基本推論テスト",
                "status": "success",
                "response": response.output_text,
                "reasoning_summary": getattr(response, 'reasoning_summary', None),
                "usage": response.usage if hasattr(response, 'usage') else None
            }
            
        except Exception as e:
            logger.error(f"Basic reasoning test failed: {e}")
            return {
                "test_name": "基本推論テスト",
                "status": "error",
                "error": str(e)
            }
    
    def test_multimodal_reasoning(self, image_url: Optional[str] = None) -> Dict[str, Any]:
        """マルチモーダル推論をテスト"""
        logger.info("Testing multimodal reasoning...")
        
        # デフォルトの画像URL（数学の図形問題）
        if not image_url:
            image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Triangle_with_notations_2.svg/500px-Triangle_with_notations_2.svg.png"
        
        try:
            response = self.client.responses.create(
                model="o3-pro",
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": "この画像の幾何学的図形について、面積と周囲長を計算してください。"},
                            {"type": "input_image", "image_url": image_url}
                        ]
                    }
                ],
                reasoning={"effort": "high"},
                include=["reasoning.encrypted_content"],
                store=False  # 永続化無効（encrypted_content使用時に必須）
            )
            
            return {
                "test_name": "マルチモーダル推論テスト",
                "status": "success",
                "response": response.output_text,
                "reasoning_summary": getattr(response, 'reasoning_summary', None),
                "usage": response.usage if hasattr(response, 'usage') else None
            }
            
        except Exception as e:
            logger.error(f"Multimodal reasoning test failed: {e}")
            return {
                "test_name": "マルチモーダル推論テスト",
                "status": "error",
                "error": str(e)
            }
    
    def test_complex_problem_solving(self) -> Dict[str, Any]:
        """複雑な問題解決能力をテスト"""
        logger.info("Testing complex problem solving...")
        
        complex_problem = """
        以下の最適化問題を解いてください：
        
        ある会社が3つの工場（A、B、C）から4つの配送センター（1、2、3、4）に製品を配送する問題です。
        
        各工場の生産能力：
        - 工場A: 100単位
        - 工場B: 150単位
        - 工場C: 120単位
        
        各配送センターの需要：
        - センター1: 80単位
        - センター2: 90単位
        - センター3: 110単位
        - センター4: 90単位
        
        配送コスト（単位あたり）：
        A→1: 4, A→2: 6, A→3: 8, A→4: 5
        B→1: 3, B→2: 4, B→3: 6, B→4: 7
        C→1: 5, C→2: 3, C→3: 4, C→4: 6
        
        総配送コストを最小化する配送計画を求めてください。
        """
        
        try:
            response = self.client.responses.create(
                model="o3-pro",
                input=complex_problem,
                reasoning={"effort": "high"},
                include=["reasoning.encrypted_content"],
                store=False  # 永続化無効（encrypted_content使用時に必須）
                # max_completion_tokens=2000  # Responses APIでは使用しない
            )
            
            return {
                "test_name": "複雑問題解決テスト",
                "status": "success",
                "response": response.output_text,
                "reasoning_summary": getattr(response, 'reasoning_summary', None),
                "usage": response.usage if hasattr(response, 'usage') else None
            }
            
        except Exception as e:
            logger.error(f"Complex problem solving test failed: {e}")
            return {
                "test_name": "複雑問題解決テスト",
                "status": "error",
                "error": str(e)
            }
    
    def test_streaming_response(self) -> Dict[str, Any]:
        """ストリーミングレスポンスをテスト"""
        logger.info("Testing streaming response...")
        
        try:
            full_response = ""
            start_time = time.time()
            
            stream = self.client.responses.create(
                model="o3-pro",
                input="フィボナッチ数列の最初の20項を計算し、各項の計算過程を説明してください。",
                reasoning={"effort": "medium"},
                stream=True
            )
            
            for event in stream:
                if hasattr(event, 'delta') and hasattr(event.delta, 'content'):
                    if event.delta.content:
                        full_response += event.delta.content
                        print(event.delta.content, end="", flush=True)
            
            end_time = time.time()
            print()  # 改行
            
            return {
                "test_name": "ストリーミングレスポンステスト",
                "status": "success",
                "response": full_response,
                "streaming_duration": end_time - start_time,
                "response_length": len(full_response)
            }
            
        except Exception as e:
            logger.error(f"Streaming response test failed: {e}")
            return {
                "test_name": "ストリーミングレスポンステスト",
                "status": "error",
                "error": str(e)
            }
    
    def test_background_processing(self) -> Dict[str, Any]:
        """バックグラウンド処理をテスト"""
        logger.info("Testing background processing...")
        
        complex_task = """
        以下の複雑な分析タスクを実行してください：
        
        1. 素数の分布パターンについて分析し、リーマン予想との関連性を考察
        2. 暗号理論における素数の重要性を説明
        3. RSA暗号アルゴリズムの数学的基盤を詳細に解説
        4. 量子コンピュータが素因数分解に与える影響を予測
        
        各項目について詳細な分析と根拠を提供してください。
        """
        
        try:
            # バックグラウンドモードで実行
            response = self.client.responses.create(
                model="o3-pro",
                input=complex_task,
                background=True,  # バックグラウンド実行
                reasoning={"effort": "high"}
            )
            
            # ステータス確認用のレスポンスID
            response_id = response.id
            
            # ポーリングでステータス確認（実際の実装では適切な間隔で確認）
            max_attempts = 10
            for attempt in range(max_attempts):
                status = self.client.responses.retrieve(response_id)
                
                if hasattr(status, 'status'):
                    if status.status == "completed":
                        return {
                            "test_name": "バックグラウンド処理テスト",
                            "status": "success",
                            "response": status.output_text if hasattr(status, 'output_text') else "Response completed",
                            "attempts": attempt + 1,
                            "response_id": response_id
                        }
                    elif status.status == "failed":
                        return {
                            "test_name": "バックグラウンド処理テスト",
                            "status": "error",
                            "error": f"Background task failed: {getattr(status, 'error', 'Unknown error')}",
                            "response_id": response_id
                        }
                
                time.sleep(2)  # 2秒待機
            
            # タイムアウト
            return {
                "test_name": "バックグラウンド処理テスト",
                "status": "timeout",
                "message": "Task did not complete within expected time",
                "response_id": response_id
            }
            
        except Exception as e:
            logger.error(f"Background processing test failed: {e}")
            return {
                "test_name": "バックグラウンド処理テスト",
                "status": "error",
                "error": str(e)
            }
    
    def test_reasoning_effort_levels(self) -> List[Dict[str, Any]]:
        """異なる推論努力レベルをテスト"""
        logger.info("Testing different reasoning effort levels...")
        
        test_problem = "次の論理パズルを解いてください：5人の人がいて、それぞれ異なる色の帽子（赤、青、緑、黄、白）を被っています。以下のヒントから各人の帽子の色を特定してください。1) Aさんは赤い帽子を被っていない。2) Bさんは青い帽子を被っている。3) Cさんは緑か黄色の帽子を被っている。4) Dさんは白い帽子を被っていない。5) Eさんは赤い帽子を被っている。"
        
        effort_levels = ["low", "medium", "high"]
        results = []
        
        for effort in effort_levels:
            try:
                start_time = time.time()
                response = self.client.responses.create(
                    model="o3-pro",
                    input=test_problem,
                    reasoning={"effort": effort}
                )
                end_time = time.time()
                
                results.append({
                    "effort_level": effort,
                    "status": "success",
                    "response": response.output_text,
                    "processing_time": end_time - start_time,
                    "usage": response.usage if hasattr(response, 'usage') else None
                })
                
            except Exception as e:
                logger.error(f"Reasoning effort test failed for {effort}: {e}")
                results.append({
                    "effort_level": effort,
                    "status": "error",
                    "error": str(e)
                })
        
        return results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """すべてのテストを実行"""
        logger.info("Running all o3-pro tests...")
        
        results = {
            "test_suite": "Azure OpenAI o3-pro Comprehensive Test",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "api_version": "2025-04-01-preview",
            "tests": []
        }
        
        # 基本推論テスト
        results["tests"].append(self.test_basic_reasoning())
        
        # マルチモーダル推論テスト
        results["tests"].append(self.test_multimodal_reasoning())
        
        # 複雑問題解決テスト
        results["tests"].append(self.test_complex_problem_solving())
        
        # ストリーミングレスポンステスト
        results["tests"].append(self.test_streaming_response())
        
        # 推論努力レベルテスト
        effort_results = self.test_reasoning_effort_levels()
        results["tests"].extend([{
            "test_name": f"推論努力レベルテスト ({r['effort_level']})",
            **r
        } for r in effort_results])
        
        # バックグラウンド処理テスト（最後に実行）
        results["tests"].append(self.test_background_processing())
        
        # 結果サマリー
        successful_tests = len([t for t in results["tests"] if t.get("status") == "success"])
        total_tests = len(results["tests"])
        
        results["summary"] = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "success_rate": f"{(successful_tests/total_tests*100):.1f}%"
        }
        
        return results

def main():
    """メイン実行関数"""
    print("=== Azure OpenAI o3-pro 機能テストプログラム ===\n")
    
    # .envファイルの再読み込み（念のため）
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        print(f".envファイルを読み込み中: {env_path}")
        load_dotenv(env_path, override=True)
    else:
        print(f"警告: .envファイルが見つかりません: {env_path}")
    
    # 環境変数デバッグ情報
    print("\n環境変数の状態:")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    print(f"  AZURE_OPENAI_ENDPOINT: {'設定済み' if endpoint else '未設定'}")
    print(f"  AZURE_OPENAI_API_KEY: {'設定済み' if api_key else '未設定'}")
    
    # 環境変数チェック
    required_vars = ["AZURE_OPENAI_ENDPOINT"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"\nError: 以下の環境変数が設定されていません: {', '.join(missing_vars)}")
        print("環境変数を.envファイルまたはシステム環境変数で設定してください。")
        print(f"\n現在の作業ディレクトリ: {os.getcwd()}")
        print(f".envファイルのパス: {env_path}")
        return
    
    # 認証方式の選択
    use_managed_identity = input("Microsoft Entra ID認証を使用しますか？ (y/n): ").lower() == 'y'
    
    if not use_managed_identity and not os.getenv("AZURE_OPENAI_API_KEY"):
        print("Error: AZURE_OPENAI_API_KEYが設定されていません。")
        return
    
    try:
        # テスト実行
        tester = O3ProTester(use_managed_identity=use_managed_identity)
        results = tester.run_all_tests()
        
        # 結果出力
        print("\n" + "="*50)
        print("テスト結果サマリー")
        print("="*50)
        print(f"実行日時: {results['timestamp']}")
        print(f"合計テスト数: {results['summary']['total_tests']}")
        print(f"成功: {results['summary']['successful_tests']}")
        print(f"失敗: {results['summary']['failed_tests']}")
        print(f"成功率: {results['summary']['success_rate']}")
        
        # 詳細結果の保存
        output_file = f"o3_pro_test_results_{int(time.time())}.json"
        import json
        
        def convert_to_serializable(obj):
            """オブジェクトをJSON serialize可能な形式に変換"""
            if hasattr(obj, 'model_dump'):
                return obj.model_dump()
            elif hasattr(obj, '__dict__'):
                return obj.__dict__
            elif isinstance(obj, (list, tuple)):
                return [convert_to_serializable(item) for item in obj]
            elif isinstance(obj, dict):
                return {key: convert_to_serializable(value) for key, value in obj.items()}
            else:
                return str(obj) if not isinstance(obj, (str, int, float, bool, type(None))) else obj
        
        try:
            serializable_results = convert_to_serializable(results)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_results, f, ensure_ascii=False, indent=2)
            print(f"\n詳細結果をファイルに保存しました: {output_file}")
        except Exception as save_error:
            print(f"\n結果保存中にエラー: {save_error}")
            print("結果はコンソール出力のみです")
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        print(f"エラー: テストの実行に失敗しました - {e}")

if __name__ == "__main__":
    main()