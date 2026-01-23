import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List
import shutil

def clean_duplicate_urls(index_path: str, knowledge_dir: str, dry_run: bool = True):
    """
    重複URLと不在ファイルのエントリをクリーンアップ
    
    Args:
        index_path: index.jsonのパス
        knowledge_dir: knowledgeディレクトリのパス  
        dry_run: Trueの場合は実際の削除を行わずレポートのみ
    """
    
    with open(index_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    archive_dir = Path(knowledge_dir) / "archive"
    
    # URLごとにエントリをグループ化
    url_to_entries: Dict[str, List[dict]] = defaultdict(list)
    
    for entry in data:
        url = entry.get('url', '')
        if url:
            url_to_entries[url].append(entry)
    
    # 削除対象のIDを収集
    ids_to_remove = set()
    files_to_delete = []
    
    print("=" * 80)
    print("クリーンアップ計画")
    print("=" * 80)
    
    # 1. 重複URLの処理
    duplicates = {url: entries for url, entries in url_to_entries.items() if len(entries) > 1}
    
    if duplicates:
        print("\n[重複URL処理]")
        for url, entries in duplicates.items():
            print(f"\nURL: {url}")
            print(f"重複数: {len(entries)}")
            
            # ファイルが存在するエントリと存在しないエントリに分類
            entries_with_file = []
            entries_without_file = []
            
            for entry in entries:
                entry_id = entry.get('id', 'NO_ID')
                archive_file = archive_dir / f"{entry_id}.md"
                
                if archive_file.exists():
                    entries_with_file.append(entry)
                else:
                    entries_without_file.append(entry)
            
            # まず、ファイルが存在しないエントリを削除対象に
            for entry in entries_without_file:
                entry_id = entry.get('id', 'NO_ID')
                print(f"  ❌ 削除: ID={entry_id} (理由: ファイル不在)")
                ids_to_remove.add(entry_id)
            
            # 次に、ファイルが存在するエントリについて、古いものを削除
            if len(entries_with_file) > 1:
                # added_atでソート(新しい順)
                entries_with_file.sort(key=lambda x: x.get('added_at', ''), reverse=True)
                
                # 最新のもの以外を削除
                for entry in entries_with_file[1:]:
                    entry_id = entry.get('id', 'NO_ID')
                    added_at = entry.get('added_at', 'NO_DATE')
                    archive_file = archive_dir / f"{entry_id}.md"
                    
                    print(f"  ❌ 削除: ID={entry_id}, 追加日時={added_at} (理由: 古い重複)")
                    ids_to_remove.add(entry_id)
                    files_to_delete.append(archive_file)
                
                # 最新のものは保持
                latest = entries_with_file[0]
                print(f"  ✅ 保持: ID={latest.get('id')}, 追加日時={latest.get('added_at')} (最新)")
    
    # 2. ファイルが存在しない項目の処理(重複でない項目)
    print("\n[ファイル不在項目処理]")
    orphan_count = 0
    for entry in data:
        entry_id = entry.get('id', 'NO_ID')
        url = entry.get('url', '')
        
        # 既に重複処理で削除対象になっているものはスキップ
        if entry_id in ids_to_remove:
            continue
        
        archive_file = archive_dir / f"{entry_id}.md"
        
        if not archive_file.exists():
            orphan_count += 1
            print(f"  ❌ 削除: ID={entry_id} (理由: ファイル不在)")
            print(f"      URL: {url}")
            ids_to_remove.add(entry_id)
    
    if orphan_count == 0:
        print("  なし")
    
    # 削除処理
    print("\n" + "=" * 80)
    print("サマリー")
    print("=" * 80)
    print(f"削除対象エントリ数: {len(ids_to_remove)}")
    print(f"削除対象ファイル数: {len(files_to_delete)}")
    
    if dry_run:
        print("\n[DRY RUN モード] 実際の削除は行いません")
        return
    
    # 実際の削除実行
    print("\n削除を実行します...")
    
    # 1. index.jsonから削除
    cleaned_data = [entry for entry in data if entry.get('id') not in ids_to_remove]
    
    # バックアップ作成
    backup_path = Path(index_path).with_suffix('.json.bak')
    shutil.copy2(index_path, backup_path)
    print(f"✅ バックアップ作成: {backup_path}")
    
    # index.json更新
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
    print(f"✅ index.json更新: {len(data)} → {len(cleaned_data)} エントリ")
    
    # 2. アーカイブファイルの削除
    for file_path in files_to_delete:
        if file_path.exists():
            file_path.unlink()
            print(f"✅ ファイル削除: {file_path.name}")
    
    print("\n完了しました！")

if __name__ == "__main__":
    import sys
    
    index_path = r"d:\projects\P010\knowledge\index.json"
    knowledge_dir = r"d:\projects\P010\knowledge"
    
    # コマンドライン引数で--executeを指定すると実際に削除
    dry_run = "--execute" not in sys.argv
    
    if dry_run:
        print("※ DRY RUNモードで実行します。実際に削除する場合は --execute を指定してください\n")
    
    clean_duplicate_urls(index_path, knowledge_dir, dry_run)
