"""
プロジェクトファイル整理スクリプト
途中過程のファイルをoldフォルダに移動し、最終的に必要なファイルのみを残す
"""

import os
import shutil
from pathlib import Path

def organize_project():
    """プロジェクトファイルを整理"""
    print("=== プロジェクトファイル整理 ===")
    
    # 現在のディレクトリ
    base_dir = Path(__file__).parent
    old_dir = base_dir / "old"
    
    # oldディレクトリ作成
    if not old_dir.exists():
        old_dir.mkdir()
        print(f"oldフォルダを作成: {old_dir}")
    else:
        print(f"oldフォルダ既存: {old_dir}")
    
    # 移動するファイル（途中過程のファイル）
    files_to_move = [
        # Azure診断・セットアップファイル
        "azure_cli_setup.py",
        "check_azure_auth.py", 
        "debug_azure_cli.py",
        "debug_env.py",
        "direct_azure_test.py",
        
        # PowerShellスクリプト
        "fix_azure_path.ps1",
        "install_azure_cli.ps1",
        "organize_files.ps1",
        
        # テスト関連
        "test_failed_parts.py",
        "quick_test_o3.py", 
        "simple_o3_test.py",
        "run_test.bat",
        "run_test.ps1",
        
        # バッチファイル
        "move_files.bat",
        
        # その他の一時ファイル
        "=1.68.0"
    ]
    
    # フォルダを移動
    folders_to_move = [
        "src",
        "tests", 
        "examples"
    ]
    
    # ファイル移動
    print("\nファイルを移動中...")
    moved_files = []
    
    for file_name in files_to_move:
        file_path = base_dir / file_name
        if file_path.exists():
            try:
                shutil.move(str(file_path), str(old_dir / file_name))
                moved_files.append(file_name)
                print(f"  OK {file_name}")
            except Exception as e:
                print(f"  NG {file_name}: Error")
        else:
            print(f"  - {file_name} (ファイルが存在しません)")
    
    # フォルダ移動
    print("\nフォルダを移動中...")
    moved_folders = []
    
    for folder_name in folders_to_move:
        folder_path = base_dir / folder_name
        if folder_path.exists() and folder_path.is_dir():
            try:
                shutil.move(str(folder_path), str(old_dir / folder_name))
                moved_folders.append(folder_name)
                print(f"  OK {folder_name}/")
            except Exception as e:
                print(f"  NG {folder_name}/: Error")
        else:
            print(f"  - {folder_name}/ (フォルダが存在しません)")
    
    # テスト結果JSONファイルを移動
    print("\nテスト結果ファイルを移動中...")
    json_files = list(base_dir.glob("o3_pro_test_results_*.json"))
    for json_file in json_files:
        try:
            shutil.move(str(json_file), str(old_dir / json_file.name))
            moved_files.append(json_file.name)
            print(f"  OK {json_file.name}")
        except Exception as e:
            print(f"  NG {json_file.name}: Error")
    
    # 整理完了レポート
    print("\n" + "="*50)
    print("整理完了レポート")
    print("="*50)
    
    print(f"\n移動されたファイル数: {len(moved_files)}")
    print(f"移動されたフォルダ数: {len(moved_folders)}")
    
    # 最終的に残ったファイル
    print("\nメインディレクトリの最終ファイル:")
    final_files = []
    for item in sorted(base_dir.iterdir()):
        if item.is_file() and item.name != "organize_project.py":
            final_files.append(item.name)
            print(f"  + {item.name}")
    
    # フォルダも表示
    print("\nメインディレクトリのフォルダ:")
    for item in sorted(base_dir.iterdir()):
        if item.is_dir() and item.name not in ["old", "venv", ".git"]:
            print(f"  + {item.name}/")
    
    # oldフォルダの内容
    print(f"\noldフォルダの内容 ({len(moved_files + moved_folders)} 項目):")
    if old_dir.exists():
        for item in sorted(old_dir.iterdir()):
            if item.is_file():
                print(f"  - old/{item.name}")
            else:
                print(f"  - old/{item.name}/")
    
    print(f"\nSUCCESS プロジェクト整理が完了しました!")
    print(f"最終的なメインファイル数: {len(final_files)}")
    
    # 最終的に必要なファイルをリスト表示
    essential_files = [
        "README_O3PRO_COMPLETE.md",
        "o3_pro_complete_toolkit.py", 
        "o3_pro_simple_demo.py",
        "azure_auth_troubleshoot.py",
        "requirements.txt",
        ".env",
        "CLAUDE.md"
    ]
    
    print(f"\n最終的に必要なファイル:")
    for file_name in essential_files:
        exists = "OK" if (base_dir / file_name).exists() else "NG"
        print(f"  {exists} {file_name}")

if __name__ == "__main__":
    organize_project()