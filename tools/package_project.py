import shutil
import os
import zipfile

def zip_project(output_filename):
    print(f"📦 Zipping project to {output_filename}...")
    
    # Excludes
    excludes = {
        'node_modules', 'venv', '__pycache__', '.git', '.idea', '.vscode',
        'logs', 'coverage', 'dist', 'build', '.DS_Store', 'start_backend.bat', 'TraderCopilot_SaleReady.zip'
    }
    
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('.'):
            # Filtering dirs in-place
            dirs[:] = [d for d in dirs if d not in excludes]
            
            for file in files:
                if file in excludes or file.endswith('.zip') or file.endswith('.log') or file.endswith('.pyc'):
                    continue
                
                # Relative path for zip
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, '.')
                
                # Skip the zip script itself and artifacts dir if needed (but we want artifacts usually)
                if 'tools/package_project.py' in arcname: 
                    continue
                    
                zipf.write(file_path, arcname)
                
    print("✅ Zip created successfully.")

if __name__ == "__main__":
    zip_project("TraderCopilot_SaleReady_Final.zip")
