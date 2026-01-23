import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List

def check_duplicate_urls(index_path: str, knowledge_dir: str):
    """index.jsonから重複URLを検出し、アーカイブファイルの存在を確認"""
    
    with open(index_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # URLごとにエントリをグループ化
    url_to_entries: Dict[str, List[dict]] = defaultdict(list)
    
    for entry in data:
        url = entry.get('url', '')
        if url:
            url_to_entries[url].append(entry)
    
    # 重複URLを検出
    duplicates = {url: entries for url, entries in url_to_entries.items() if len(entries) > 1}
    
    # 結果の出力
    print("=" * 80)
    print("重複URL検出レポート")
    print("=" * 80)
    
    if not duplicates:
        print("\n重複URLは見つかりませんでした。")
    else:
        print(f"\n{len(duplicates)}個の重複URLが見つかりました。\n")
        
        for url, entries in duplicates.items():
            print(f"\nURL: {url}")
            print(f"重複数: {len(entries)}")
            
            for i, entry in enumerate(entries, 1):
                entry_id = entry.get('id', 'NO_ID')
                added_at = entry.get('added_at', 'NO_DATE')
                title = entry.get('title', 'NO_TITLE')
                
                # アーカイブファイルの存在確認
                archive_file = Path(knowledge_dir) / "archive" / f"{entry_id}.md"
                file_exists = archive_file.exists()
                
                print(f"  [{i}] ID: {entry_id}")
                print(f"      タイトル: {title}")
                print(f"      追加日時: {added_at}")
                print(f"      ファイル: {'存在' if file_exists else '存在しない ❌'}")
    
    # ファイルが存在しない項目のリスト
    print("\n" + "=" * 80)
    print("ファイルが存在しない項目")
    print("=" * 80)
    
    missing_files = []
    for entry in data:
        entry_id = entry.get('id', 'NO_ID')
        archive_file = Path(knowledge_dir) / "archive" / f"{entry_id}.md"
        if not archive_file.exists():
            missing_files.append(entry)
            url = entry.get('url', 'NO_URL')
            title = entry.get('title', 'NO_TITLE')
            print(f"\nID: {entry_id}")
            print(f"Title: {title}")
            print(f"URL: {url}")
    
    print("\n" + "=" * 80)
    print("サマリー")
    print("=" * 80)
    print(f"総エントリ数: {len(data)}")
    print(f"重複URL数: {len(duplicates)}")
    print(f"ファイルが存在しない項目数: {len(missing_files)}")
    
    return duplicates, missing_files

if __name__ == "__main__":
    index_path = r"d:\projects\P010\knowledge\index.json"
    knowledge_dir = r"d:\projects\P010\knowledge"
    
    check_duplicate_urls(index_path, knowledge_dir)
