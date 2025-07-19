"""
シンプルなプロジェクト整理
重要なファイルを特定し、不要なファイルをリスト化
"""

import os
from pathlib import Path

def main():
    print("=== プロジェクト整理状況 ===")
    
    base_dir = Path(__file__).parent
    
    # 最終的に必要なファイル
    essential_files = {
        "README_O3PRO_COMPLETE.md": "完全ガイドドキュメント",
        "o3_pro_complete_toolkit.py": "完全版ツールキット", 
        "o3_pro_simple_demo.py": "動作確認済みデモ",
        "azure_auth_troubleshoot.py": "Azure認証診断ツール",
        "requirements.txt": "依存関係",
        "CLAUDE.md": "プロジェクト設定",
        ".env": "環境変数（ユーザー作成）"
    }
    
    # 重要だが必須ではないファイル
    optional_files = {
        "README.md": "元のREADME",
        ".gitignore": "Git設定",
        ".env.example": "環境変数サンプル"
    }
    
    # 移動対象（不要な途中ファイル）
    files_to_archive = [
        "azure_cli_setup.py",
        "check_azure_auth.py", 
        "debug_azure_cli.py",
        "debug_env.py",
        "direct_azure_test.py",
        "fix_azure_path.ps1",
        "install_azure_cli.ps1",
        "organize_files.ps1",
        "test_failed_parts.py",
        "quick_test_o3.py", 
        "simple_o3_test.py",
        "run_test.bat",
        "run_test.ps1",
        "move_files.bat",
        "organize_project.py",
        "simple_cleanup.py",
        "=1.68.0"
    ]
    
    # JSON結果ファイル
    json_pattern = "o3_pro_test_results_*.json"
    
    print("\n必須ファイル状況:")
    for file_name, description in essential_files.items():
        file_path = base_dir / file_name
        exists = "OK" if file_path.exists() else "NG"
        print(f"  {exists} {file_name} - {description}")
    
    print("\nオプションファイル状況:")
    for file_name, description in optional_files.items():
        file_path = base_dir / file_name
        exists = "OK" if file_path.exists() else "--"
        print(f"  {exists} {file_name} - {description}")
    
    print("\n移動対象ファイル:")
    existing_archive_files = []
    for file_name in files_to_archive:
        file_path = base_dir / file_name
        if file_path.exists():
            existing_archive_files.append(file_name)
            print(f"  - {file_name}")
    
    # JSONファイル
    json_files = list(base_dir.glob(json_pattern))
    if json_files:
        print(f"\nテスト結果ファイル ({len(json_files)}個):")
        for json_file in json_files:
            print(f"  - {json_file.name}")
    
    # フォルダ
    folders_to_archive = ["src", "tests", "examples"]
    existing_folders = []
    for folder_name in folders_to_archive:
        folder_path = base_dir / folder_name
        if folder_path.exists():
            existing_folders.append(folder_name)
    
    if existing_folders:
        print(f"\n移動対象フォルダ:")
        for folder_name in existing_folders:
            print(f"  - {folder_name}/")
    
    # 現在のメインディレクトリファイル数
    all_files = [f for f in base_dir.iterdir() if f.is_file()]
    print(f"\n現在のメインディレクトリファイル数: {len(all_files)}")
    print(f"移動対象ファイル数: {len(existing_archive_files) + len(json_files)}")
    print(f"移動対象フォルダ数: {len(existing_folders)}")
    
    # 整理後の予想
    remaining_files = len(all_files) - len(existing_archive_files) - len(json_files)
    print(f"整理後の予想ファイル数: {remaining_files}")
    
    print("\n次のステップ:")
    print("1. 手動でoldフォルダにファイル移動")
    print("2. または以下のコマンドを実行:")
    print("   for file in $(ls | grep -E '(azure_cli_setup|check_azure|debug_|direct_|fix_|install_|organize|test_failed|quick_test|simple_o3|run_test|move_files|=1.68.0)'); do mv \"$file\" old/; done")

if __name__ == "__main__":
    main()