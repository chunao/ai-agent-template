import json
import argparse
import os
import sys
import subprocess
import time

# Helper logic to resolve paths
INDEX_PATH = 'knowledge/index.json'

def check_id_exists(target_id):
    """
    Checks if the target_id exists in INDEX_PATH.
    Returns True if found, False otherwise.
    """
    if not os.path.exists(INDEX_PATH):
        return False
    try:
        with open(INDEX_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, list):
                return False
            for item in data:
                if item.get('id') == target_id:
                    return True
    except Exception as e:
        # If file is locked or invalid JSON (temporarily), return False to retry
        print(f"Warning: Error reading index.json: {e}")
        return False
    return False

def main():
    # We parse known args to get the ID for verification.
    # The rest are passed appropriately to the subprocess.
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--id', required=True, help='Article ID to verify')
    
    # parse_known_args allows us to ignore other flags meant for add_metadata.py
    args, unknown = parser.parse_known_args()
    target_id = args.id

    # Construct path to the actual worker script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    worker_script = os.path.join(current_dir, 'add_metadata.py')

    max_retries = 3
    
    for attempt in range(max_retries):
        print(f"--- Attempt {attempt + 1}/{max_retries}: Registering metadata ---")
        
        # Execute add_metadata.py with ALL original arguments
        # sys.argv[1:] contains all arguments passed to this script
        cmd = [sys.executable, worker_script] + sys.argv[1:]
        
        try:
            subprocess.run(cmd, check=False)
        except Exception as e:
            print(f"Error executing registration command: {e}")
            # We don't exit here, we verify anyway as per instructions (checking file is the truth)

        print("Waiting 10 seconds before starting verification checks...")
        time.sleep(10)

        # Verification Loop (approx 1 minute window)
        # We already waited 10s. The user said "check is executed after 10s, if not confirmed for max 1 min..."
        # I'll treat "max 1 min" as the timeout for the loop.
        
        verification_timeout = 60
        start_time = time.time()
        verified = False

        print(f"Checking {INDEX_PATH} for ID: {target_id}...")
        
        while (time.time() - start_time) < verification_timeout:
            if check_id_exists(target_id):
                verified = True
                break
            
            # Wait a bit before next check
            time.sleep(5)
            print(".", end="", flush=True)
            
        print() # Newline

        if verified:
            print(f"SUCCESS: ID {target_id} verified in {INDEX_PATH}.")
            sys.exit(0)
        else:
            print(f"FAILURE: ID {target_id} NOT found in {INDEX_PATH} after ~{verification_timeout} seconds.")
            if attempt < max_retries - 1:
                print("Retrying registration...")
            else:
                print("Max retries reached. Registration failed.")
                sys.exit(1)

if __name__ == '__main__':
    main()
