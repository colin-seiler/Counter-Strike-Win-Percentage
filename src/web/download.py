from curl_cffi import requests
import os
import subprocess
import time

from src.web.constants import HEADERS, MAX_ATTEMPTS
from src.utils import delete_file

def verify_rar(rar_path):
    result = subprocess.run(
        ['unar', '-t', rar_path],  # -t = test archive (shows contents without extracting)
        capture_output=True,
        text=True
    )
    return result.returncode == 0

def download_file(url, output_path):
    attempt = 1

    while attempt <= MAX_ATTEMPTS:
        try:
            print(f"Downloading: {url} - Attempt {attempt}")
        
            r = requests.get(url, stream=True, impersonate="chrome", 
                        headers=HEADERS, timeout=1200)
            r.raise_for_status()
        
            # Get expected size from headers
            expected_size = int(r.headers.get('content-length', 0))
            print(f"Expected size: {expected_size:,} bytes")
        
            with open(output_path, 'wb') as f:
                downloaded = 0
                for chunk in r.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
    
            # Verify download completed
            actual_size = os.path.getsize(output_path)
            print(f"Downloaded: {actual_size:,} bytes")
            
            if expected_size > 0 and actual_size != expected_size:
                raise Exception(f"Incomplete download: {actual_size}/{expected_size} bytes")
            else:
                if not verify_rar(output_path):
                    raise Exception(f"RAR file is corrupt or incomplete at {output_path}")
                
            print("✅ Download complete and verified")
            return output_path
        except Exception as e:
            print(f'❌ Attempt {attempt} Failed: {e}')
            delete = delete_file(output_path)
            print(f'Corrupted File Deleted: {delete}')
            attempt += 1
            time.sleep(attempt * 5)
    
    return None #if max tries reached