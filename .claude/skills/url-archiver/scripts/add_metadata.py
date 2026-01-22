import json
import argparse
import os
from datetime import datetime

INDEX_PATH = 'knowledge/index.json'

def main():
    parser = argparse.ArgumentParser(description='Add metadata to knowledge index')
    parser.add_argument('--id', required=True, help='Article ID (YYYYMMDD_UUID)')
    parser.add_argument('--title', required=True, help='Article Title')
    parser.add_argument('--url', required=True, help='Source URL')
    parser.add_argument('--description', help='Brief description')
    parser.add_argument('--tags', help='Pipe-separated tags (e.g. tag1|tag2)')
    parser.add_argument('--published_at', help='Original publication date (YYYY-MM-DD)')
    
    # Normalized Condition Fields (Pipe-separated for sentence support)
    parser.add_argument('--use_cases', help='Pipe-separated use cases')
    parser.add_argument('--anti_cases', help='Pipe-separated anti-cases')
    parser.add_argument('--prerequisites', help='Pipe-separated prerequisites')
    parser.add_argument('--decision_triggers', help='Pipe-separated decision triggers')
    parser.add_argument('--code_snippets', help='Pipe-separated code snippet descriptions')

    args = parser.parse_args()

    entry = {
        'id': args.id,
        'title': args.title,
        'url': args.url,
        'added_at': datetime.now().isoformat(),
    }
    
    if args.description:
        entry['description'] = args.description
    
    if args.published_at:
        entry['published_at'] = args.published_at
    
    # Helper to split by pipe
    def split_pipe(val):
        if not val:
            return None
        return [x.strip() for x in val.split('|') if x.strip()]

    if args.tags:
        entry['tags'] = split_pipe(args.tags)

    if args.use_cases:
        entry['use_cases'] = split_pipe(args.use_cases)

    if args.anti_cases:
        entry['anti_cases'] = split_pipe(args.anti_cases)

    if args.prerequisites:
        entry['prerequisites'] = split_pipe(args.prerequisites)

    if args.decision_triggers:
        entry['decision_triggers'] = split_pipe(args.decision_triggers)

    if args.code_snippets:
        entry['code_snippets'] = split_pipe(args.code_snippets)

    # Ensure directory exists
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)

    # Load existing
    data = []
    if os.path.exists(INDEX_PATH):
        try:
            with open(INDEX_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: {INDEX_PATH} is invalid JSON. Aborting to prevent data loss. Please fix the file manually.")
            return

    # Check for duplicates? Maybe by ID.
    existing_ids = {item.get('id') for item in data}
    if args.id in existing_ids:
        print(f"Error: ID {args.id} already exists.")
        return

    data.append(entry)

    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully added {args.id} to {INDEX_PATH}")

if __name__ == '__main__':
    main()
