from curl_cffi import requests
import os

from src.web.constants import HEADERS

def download_file(url, output_path):
    print(f"Downloading: {url}")
    
    r = requests.get(url, stream=True, impersonate="chrome", 
                     headers=HEADERS, timeout=600)
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
                
                if expected_size > 0:
                    percent = (downloaded / expected_size) * 100
                    print(f"\rProgress: {percent:.1f}%", end='')
    
    print()
    
    # Verify download completed
    actual_size = os.path.getsize(output_path)
    print(f"Downloaded: {actual_size:,} bytes")
    
    if expected_size > 0 and actual_size < expected_size:
        os.remove(output_path)  # Delete corrupt file
        raise Exception(f"Incomplete download: {actual_size}/{expected_size} bytes")
    
    print("✅ Download complete and verified")
    return output_path