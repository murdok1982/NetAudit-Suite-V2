import subprocess
import json
import os

def check_username_sherlock(username: str):
    """
    Wraps Sherlock to check for username presence across platforms.
    Note: Requires sherlock to be installed and in PATH.
    """
    try:
        # Running sherlock with json output to a temporary file
        result_file = f"data/sherlock_{username}.json"
        cmd = ["sherlock", username, "--json", result_file, "--timeout", "5"]
        
        # In a real environment, we'd use a safer execution or a container
        subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if os.path.exists(result_file):
            with open(result_file, 'r') as f:
                data = json.load(f)
            # Cleanup
            # os.remove(result_file)
            return data
        return {}
    except Exception as e:
        print(f"Sherlock error: {e}")
        return {"error": str(e)}
