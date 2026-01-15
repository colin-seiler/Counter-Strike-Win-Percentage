import subprocess
import os
import glob

from src.utils import delete_file, clear_demos

def extract_with_unar(rar_path, extract_to="data/demos/"):
    #Extract .dem files from rar
    os.makedirs(extract_to, exist_ok=True)
    print(f"🔍 DEBUG: rar_path = {rar_path}")
    print(f"🔍 DEBUG: File exists? {os.path.exists(rar_path)}")
    print(f"🔍 DEBUG: File size: {os.path.getsize(rar_path) if os.path.exists(rar_path) else 'N/A'}")

    # DEBUG: List contents of RAR before extraction
    print(f"📦 Contents of {rar_path}:")
    list_result = subprocess.run(
        ['unar', '-t', rar_path],  # -t = test archive (shows contents without extracting)
        capture_output=True,
        text=True
    )
    print(list_result.stdout)
    if list_result.stderr:
        print("STDERR:", list_result.stderr)

    clear_demos(extract_to)
    
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
        deleted = delete_file(rar_path)
        return []