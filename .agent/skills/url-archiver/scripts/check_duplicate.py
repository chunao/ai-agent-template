import json
import argparse
import os
import sys

INDEX_PATH = 'knowledge/index.json'

def main():
    parser = argparse.ArgumentParser(description='Check if URL exists in knowledge index')
    parser.add_argument('--url', required=True, help='URL to check')
    args = parser.parse_args()

    if not os.path.exists(INDEX_PATH):
        # Index doesn't exist, so no duplicates
        sys.exit(0)

    try:
        with open(INDEX_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        # Invalid JSON, treat as empty
        sys.exit(0)

    # Normalize URL for comparison (basic)
    target_url = args.url.strip()
    
    # Check for exact match (could be improved with normalization logic if needed)
    found_item = None
    for item in data:
        if item.get('url') == target_url:
            found_item = item
            break
    
    if found_item:
        # Output detailed information in JSON format
        duplicate_info = {
            'id': found_item.get('id'),
            'url': found_item.get('url'),
            'file': f"knowledge/archive/{found_item.get('id')}.md",
            'title': found_item.get('title')
        }
        print(json.dumps(duplicate_info, ensure_ascii=False))
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()
