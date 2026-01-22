import argparse
import hashlib
import datetime
import sys

def generate_id(url):
    # Use current date as prefix
    today = datetime.datetime.now().strftime("%Y%m%d")
    
    # Calculate MD5 of the URL
    # This ensures consistency: same URL on same day -> same ID.
    url_md5 = hashlib.md5(url.encode('utf-8')).hexdigest()
    
    # Take first 6 characters short hash
    short_hash = url_md5[:6]
    
    return f"{today}_{short_hash}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a standardized ID for the URL archive.')
    parser.add_argument('--url', required=True, help='The URL being archived')
    args = parser.parse_args()
    
    try:
        print(generate_id(args.url))
    except Exception as e:
        print(f"Error generating ID: {e}", file=sys.stderr)
        sys.exit(1)
