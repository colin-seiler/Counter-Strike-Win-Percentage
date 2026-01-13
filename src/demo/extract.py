import subprocess
import os
import glob

from src.utils import delete_file

def extract_with_unar(rar_path, extract_to="./demos"):
    #Extract .dem files from rar
    os.makedirs(extract_to, exist_ok=True)
    
    try:
        result = subprocess.run(
            ['unar', '-f', '-D', '-o', extract_to, '-q', rar_path],
            check=True,
            capture_output=True,
            text=True
        )
        
        deleted = delete_file(rar_path)
        
        extracted_files = glob.glob(os.path.join(extract_to, "*.dem"))
        return extracted_files

    except subprocess.CalledProcessError as e:
        print(f"❌ unar failed: {e.stderr}")
        return []