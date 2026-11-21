"""
Utility script to create the clean distribution ZIP archive.
Excludes virtual environments, caches, and development artifacts.
"""

import os
import zipfile

OUTPUT_ZIP = "student-performance-analytics-submission.zip"
EXCLUDE_DIRS = {
    ".venv", "venv", "env", "__pycache__", ".pytest_cache",
    ".git", ".vscode", ".idea", "htmlcov"
}
EXCLUDE_FILES = {
    OUTPUT_ZIP, ".coverage", "Thumbs.db", ".DS_Store"
}

def create_zip():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    zip_path = os.path.join(base_dir, OUTPUT_ZIP)

    print(f"Packaging project from: {base_dir}")
    print(f"Creating submission archive: {zip_path}")

    file_count = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(base_dir):
            # Prune excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for file in files:
                if file in EXCLUDE_FILES or file.endswith(".pyc"):
                    continue

                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_dir)
                zip_file.write(full_path, rel_path)
                file_count += 1
                print(f"  + Added: {rel_path}")

    size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print("=" * 60)
    print(f"SUCCESS: Created {OUTPUT_ZIP} ({file_count} files, {size_mb:.2f} MB)")
    print("Project package is ready for distribution and deployment.")
    print("=" * 60)

if __name__ == "__main__":
    create_zip()
