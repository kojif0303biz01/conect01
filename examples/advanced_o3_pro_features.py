"""
Azure OpenAI o3-pro 高度な機能デモ

このファイルは、o3-proモデルの高度な機能を実演するサンプルコードです。
- 複雑な推論タスク
- バックグラウンド処理
- ツール統合
- マルチモーダル処理
"""

import os
import json
import time
import asyncio
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

class AdvancedO3ProDemo:
    """o3-pro高度機能デモンストレーションクラス"""
    
    def __init__(self, use_managed_identity: bool = False):
        """初期化"""
        load_dotenv()
        self.client = self._create_client(use_managed_identity)
    
    def _create_client(self, use_managed_identity: bool) -> AzureOpenAI:
        """クライアント作成"""
        if use_managed_identity:
            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(), 
                "https://cognitiveservices.azure.com/.default"
            )
            return AzureOpenAI(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                azure_ad_token_provider=token_provider,
                api_version="2025-04-01-preview"
            )
        else:
            return AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_version="2025-04-01-preview"
            )
    
    def scientific_reasoning_demo(self) -> Dict[str, Any]:
        """科学的推論のデモ"""
        print("=== 科学的推論デモ ===")
        
        scientific_problem = """
        以下の物理学問題を解いてください：
        
        質量50kgの物体が、摩擦係数μ=0.3の水平面上で、
        100Nの力で30度の角度で引っ張られています。
        
        1. 物体にかかる全ての力を図示・説明
        2. 運動方程式を立てる
        3. 加速度を計算
        4. 3秒後の速度と移動距離を求める
        
        各ステップで物理法則の根拠も説明してください。
        """
        
        response = self.client.responses.create(
            model="o3-pro",
            input=scientific_problem,
            reasoning={"effort": "high"},
            include=["reasoning.summary"],
            max_completion_tokens=2000
        )
        
        print("問題:", scientific_problem.strip())
        print("\n回答:")
        print(response.output_text)
        
        return {
            "demo": "scientific_reasoning",
            "input": scientific_problem,
            "output": response.output_text,
            "reasoning_summary": getattr(response, 'reasoning_summary', None)
        }
    
    def mathematical_proof_demo(self) -> Dict[str, Any]:
        """数学的証明のデモ"""
        print("\n=== 数学的証明デモ ===")
        
        proof_problem = """
        次の定理を厳密に証明してください：
        
        【定理】平方根の無理性
        √2は無理数である。
        
        要求事項：
        1. 背理法を用いた厳密な証明
        2. 各論理ステップの明確な説明
        3. 使用する数学的原理の明示
        4. 証明の構造の解説
        """
        
        response = self.client.responses.create(
            model="o3-pro",
            input=proof_problem,
            reasoning={"effort": "high"},
            include=["reasoning.summary"]
        )
        
        print("証明問題:", proof_problem.strip())
        print("\n証明:")
        print(response.output_text)
        
        return {
            "demo": "mathematical_proof",
            "input": proof_problem,
            "output": response.output_text
        }
    
    def algorithm_design_demo(self) -> Dict[str, Any]:
        """アルゴリズム設計のデモ"""
        print("\n=== アルゴリズム設計デモ ===")
        
        algorithm_task = """
        以下の最適化問題に対する効率的なアルゴリズムを設計してください：
        
        【問題】動的な配送経路最適化
        - N個の配送地点（座標付き）
        - 複数の配送車両（容量制限あり）
        - 時間窓制約（各地点に特定時間内に到着必須）
        - 動的需要変化（リアルタイムで新規注文追加）
        
        要求事項：
        1. 効率的なアルゴリズムの設計
        2. 時間計算量の分析
        3. 疑似コードの提供
        4. 実装時の注意点
        5. スケーラビリティの考慮
        """
        
        response = self.client.responses.create(
            model="o3-pro",
            input=algorithm_task,
            reasoning={"effort": "high"},
            max_completion_tokens=2500
        )
        
        print("アルゴリズム設計タスク:", algorithm_task.strip())
        print("\nアルゴリズム設計:")
        print(response.output_text)
        
        return {
            "demo": "algorithm_design",
            "input": algorithm_task,
            "output": response.output_text
        }
    
    def code_generation_demo(self) -> Dict[str, Any]:
        """高度なコード生成のデモ"""
        print("\n=== 高度なコード生成デモ ===")
        
        code_task = """
        以下の要件を満たすPythonクラスを設計・実装してください：
        
        【要件】分散キャッシュシステム
        - 一貫性ハッシュリングによるデータ分散
        - レプリケーション（複製数3）
        - 故障検知と自動復旧
        - 非同期I/O対応
        - メトリクス収集機能
        
        実装内容：
        1. 完全なクラス設計（インターフェース定義含む）
        2. 主要メソッドの実装
        3. エラーハンドリング
        4. パフォーマンス考慮事項
        5. テストケースの例
        """
        
        response = self.client.responses.create(
            model="o3-pro",
            input=code_task,
            reasoning={"effort": "high"},
            max_completion_tokens=3000
        )
        
        print("コード生成タスク:", code_task.strip())
        print("\n生成されたコード:")
        print(response.output_text)
        
        return {
            "demo": "code_generation",
            "input": code_task,
            "output": response.output_text
        }
    
    def strategic_analysis_demo(self) -> Dict[str, Any]:
        """戦略分析のデモ"""
        print("\n=== 戦略分析デモ ===")
        
        strategy_scenario = """
        以下のビジネスシナリオについて包括的な戦略分析を行ってください：
        
        【シナリオ】新技術スタートアップの市場参入戦略
        - 分野：生成AI技術を活用したエンタープライズソリューション
        - 競合：大手テック企業（Google, Microsoft, Amazon）
        - 資金調達：シリーズA（$10M調達済み）
        - チーム：技術者15名、ビジネス5名
        
        分析項目：
        1. 市場機会分析（TAM/SAM/SOM）
        2. 競合分析とポジショニング戦略
        3. プロダクト差別化戦略
        4. Go-to-Market戦略
        5. リスク評価と緩和策
        6. 3年間の成長シナリオ
        7. 投資回収計画
        """
        
        response = self.client.responses.create(
            model="o3-pro",
            input=strategy_scenario,
            reasoning={"effort": "high"},
            max_completion_tokens=3000
        )
        
        print("戦略分析シナリオ:", strategy_scenario.strip())
        print("\n戦略分析結果:")
        print(response.output_text)
        
        return {
            "demo": "strategic_analysis",
            "input": strategy_scenario,
            "output": response.output_text
        }
    
    def background_processing_demo(self) -> Dict[str, Any]:
        """バックグラウンド処理のデモ"""
        print("\n=== バックグラウンド処理デモ ===")
        
        complex_research_task = """
        以下の学術研究タスクを実行してください：
        
        【研究テーマ】量子コンピュータと暗号技術の将来
        
        研究項目：
        1. 量子アルゴリズム（Shor、Grover等）の詳細分析
        2. 現在の暗号技術（RSA、ECC等）への影響評価
        3. 耐量子暗号の技術動向と標準化状況
        4. 産業界への実用的影響とタイムライン
        5. 政策・規制面での考慮事項
        6. 今後10年の技術発展予測
        7. 推奨される対策・準備事項
        
        各項目について学術的根拠と最新の研究成果を含めて詳細に分析してください。
        """
        
        print("複雑なタスクをバックグラウンドで実行中...")
        
        # バックグラウンドモードで実行
        response = self.client.responses.create(
            model="o3-pro",
            input=complex_research_task,
            background=True,
            reasoning={"effort": "high"}
        )
        
        response_id = response.id
        print(f"バックグラウンドタスクID: {response_id}")
        
        # ステータス監視
        max_attempts = 15
        for attempt in range(max_attempts):
            print(f"ステータス確認 {attempt + 1}/{max_attempts}...")
            
            status = self.client.responses.retrieve(response_id)
            
            if hasattr(status, 'status'):
                print(f"現在のステータス: {status.status}")
                
                if status.status == "completed":
                    print("\nバックグラウンドタスク完了!")
                    print("研究結果:")
                    print(status.output_text if hasattr(status, 'output_text') else "結果取得エラー")
                    
                    return {
                        "demo": "background_processing",
                        "input": complex_research_task,
                        "output": status.output_text if hasattr(status, 'output_text') else None,
                        "response_id": response_id,
                        "attempts": attempt + 1
                    }
                elif status.status == "failed":
                    print(f"タスク失敗: {getattr(status, 'error', 'Unknown error')}")
                    return {
                        "demo": "background_processing",
                        "status": "failed",
                        "error": getattr(status, 'error', 'Unknown error')
                    }
            
            time.sleep(5)  # 5秒待機
        
        print("タイムアウト: タスクが完了しませんでした")
        return {
            "demo": "background_processing",
            "status": "timeout",
            "response_id": response_id
        }
    
    def run_all_demos(self) -> List[Dict[str, Any]]:
        """すべてのデモを実行"""
        print("=== Azure OpenAI o3-pro 高度機能デモンストレーション ===\n")
        
        demos = []
        
        try:
            # 科学的推論
            demos.append(self.scientific_reasoning_demo())
            
            # 数学的証明
            demos.append(self.mathematical_proof_demo())
            
            # アルゴリズム設計
            demos.append(self.algorithm_design_demo())
            
            # コード生成
            demos.append(self.code_generation_demo())
            
            # 戦略分析
            demos.append(self.strategic_analysis_demo())
            
            # バックグラウンド処理（最後に実行）
            demos.append(self.background_processing_demo())
            
        except Exception as e:
            print(f"デモ実行中にエラーが発生しました: {e}")
            demos.append({
                "demo": "error",
                "error": str(e)
            })
        
        return demos

def main():
    """メイン実行関数"""
    print("Azure OpenAI o3-pro 高度機能デモを開始します...\n")
    
    # 環境変数チェック
    if not os.getenv("AZURE_OPENAI_ENDPOINT"):
        print("Error: AZURE_OPENAI_ENDPOINT が設定されていません")
        return
    
    # 認証方式選択
    use_managed_identity = input("Microsoft Entra ID認証を使用しますか？ (y/n): ").lower() == 'y'
    
    if not use_managed_identity and not os.getenv("AZURE_OPENAI_API_KEY"):
        print("Error: AZURE_OPENAI_API_KEY が設定されていません")
        return
    
    try:
        # デモ実行
        demo = AdvancedO3ProDemo(use_managed_identity=use_managed_identity)
        results = demo.run_all_demos()
        
        # 結果保存
        timestamp = int(time.time())
        output_file = f"o3_pro_advanced_demo_results_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\nデモ結果を保存しました: {output_file}")
        print(f"実行されたデモ数: {len(results)}")
        
    except Exception as e:
        print(f"デモの実行に失敗しました: {e}")

if __name__ == "__main__":
    main()