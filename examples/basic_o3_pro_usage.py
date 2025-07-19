"""
Azure OpenAI o3-pro 基本使用例

このファイルは、o3-proモデルの基本的な使い方を示すサンプルコードです。
最新のResponses APIを使用した簡単な例から始めます。
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from openai import AzureOpenAI

# .envファイルの明示的な読み込み
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path, override=True)

def basic_reasoning_example():
    """基本的な推論タスクの例"""
    
    # クライアント初期化
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version="2025-04-01-preview"
    )
    
    # 基本的な推論タスク
    response = client.responses.create(
        model="o3-pro",
        input="2つの異なる素数の積が35になる組み合わせを見つけ、その理由を説明してください。",
        reasoning={"effort": "medium"}
    )
    
    print("問題: 2つの異なる素数の積が35になる組み合わせを見つけ、その理由を説明してください。")
    print(f"回答: {response.output_text}")
    
    if hasattr(response, 'usage'):
        print(f"使用量: {response.usage}")

def multimodal_example():
    """マルチモーダル（テキスト＋画像）の例"""
    
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version="2025-04-01-preview"
    )
    
    # 画像解析タスク
    response = client.responses.create(
        model="o3-pro",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "この数学の図を分析し、解法を詳しく説明してください。"},
                    {"type": "input_image", "image_url": "https://example.com/math_diagram.png"}
                ]
            }
        ],
        reasoning={"effort": "high"}
    )
    
    print("マルチモーダル分析結果:")
    print(response.output_text)

def streaming_example():
    """ストリーミングレスポンスの例"""
    
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version="2025-04-01-preview"
    )
    
    print("ストリーミング出力開始:")
    print("問題: ピタゴラスの定理を証明してください。")
    print("回答: ", end="")
    
    # ストリーミングで回答を取得
    stream = client.responses.create(
        model="o3-pro",
        input="ピタゴラスの定理（a² + b² = c²）を幾何学的に証明してください。ステップごとに詳しく説明してください。",
        reasoning={"effort": "high"},
        stream=True
    )
    
    for event in stream:
        if hasattr(event, 'delta') and hasattr(event.delta, 'content'):
            if event.delta.content:
                print(event.delta.content, end="", flush=True)
    
    print()  # 改行

def effort_level_comparison():
    """異なる推論努力レベルの比較"""
    
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version="2025-04-01-preview"
    )
    
    problem = "x³ - 6x² + 11x - 6 = 0 の解をすべて求め、因数分解の過程を説明してください。"
    
    effort_levels = ["low", "medium", "high"]
    
    for effort in effort_levels:
        print(f"\n=== 推論努力レベル: {effort} ===")
        
        response = client.responses.create(
            model="o3-pro",
            input=problem,
            reasoning={"effort": effort}
        )
        
        print(f"回答: {response.output_text}")
        
        if hasattr(response, 'usage'):
            print(f"使用量: {response.usage}")

if __name__ == "__main__":
    print("=== Azure OpenAI o3-pro 基本使用例 ===\n")
    
    # 環境変数チェック
    if not os.getenv("AZURE_OPENAI_API_KEY") or not os.getenv("AZURE_OPENAI_ENDPOINT"):
        print("Error: 環境変数 AZURE_OPENAI_API_KEY と AZURE_OPENAI_ENDPOINT を設定してください。")
        exit(1)
    
    try:
        # 基本的な推論例
        print("1. 基本的な推論例")
        basic_reasoning_example()
        
        print("\n" + "="*50 + "\n")
        
        # ストリーミング例
        print("2. ストリーミングレスポンス例")
        streaming_example()
        
        print("\n" + "="*50 + "\n")
        
        # 推論努力レベル比較
        print("3. 推論努力レベル比較")
        effort_level_comparison()
        
        # マルチモーダル例（オプション）
        # print("\n" + "="*50 + "\n")
        # print("4. マルチモーダル例")
        # multimodal_example()
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        print("o3-proモデルがデプロイされていることを確認してください。")