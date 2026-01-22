import json
import argparse
import os
import sys

INDEX_PATH = 'knowledge/index.json'

def main():
    parser = argparse.ArgumentParser(description='Remove archived article by ID')
    parser.add_argument('--id', required=True, help='Article ID to remove (YYYYMMDD_UUID)')
    args = parser.parse_args()

    archive_file = f"knowledge/archive/{args.id}.md"
    
    # Check if archive file exists
    if not os.path.exists(archive_file):
        print(f"Error: Archive file not found: {archive_file}")
        sys.exit(1)
    
    # Check if index exists
    if not os.path.exists(INDEX_PATH):
        print(f"Error: Index file not found: {INDEX_PATH}")
        sys.exit(1)
    
    # Load index
    try:
        with open(INDEX_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: {INDEX_PATH} is invalid JSON. Cannot proceed.")
        sys.exit(1)
    
    # Find and remove the entry
    original_length = len(data)
    data = [item for item in data if item.get('id') != args.id]
    
    if len(data) == original_length:
        print(f"Warning: ID {args.id} not found in index, but archive file exists.")
    
    # Delete archive file
    try:
        os.remove(archive_file)
        print(f"Deleted archive file: {archive_file}")
    except Exception as e:
        print(f"Error deleting archive file: {e}")
        sys.exit(1)
    
    # Update index
    try:
        with open(INDEX_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Updated index: removed entry for {args.id}")
    except Exception as e:
        print(f"Error updating index: {e}")
        sys.exit(1)
    
    print(f"Successfully removed archive: {args.id}")

if __name__ == '__main__':
    main()
