#!/usr/bin/env python3
"""
モジュール統合テスト
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_reasoning():
    """基本推論テスト"""
    try:
        from core.azure_auth import O3ProConfig, O3ProClient
        from handlers import ReasoningHandler
        
        config = O3ProConfig()
        if not config.validate():
            return False
        
        client = O3ProClient(config)
        if not client.is_ready():
            return False
        
        handler = ReasoningHandler(client)
        result = handler.basic_reasoning("1+1は何ですか？", effort="low")
        
        return result["success"]
        
    except Exception as e:
        print(f"エラー: {e}")
        return False

def main():
    print("=== 基本推論テスト ===")
    if test_reasoning():
        print("✅ テスト成功")
    else:
        print("❌ テスト失敗")

if __name__ == "__main__":
    main()