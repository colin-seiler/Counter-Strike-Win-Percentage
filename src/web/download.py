from curl_cffi import requests

from src.web.constants import HEADERS

def download_file(url, output_path): 
    #Download match RAR from HLTV
    with requests.get(url, stream=True, impersonate="chrome", headers=HEADERS) as r:
        r.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return output_path