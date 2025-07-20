#!/usr/bin/env python3
"""Setup Wizard for FonDeDeNaJa project."""
import os
import sys
import argparse
import shutil
from pathlib import Path


def check_file(path: Path) -> bool:
    if path.exists():
        print(f"[OK]     {path}")
        return True
    else:
        print(f"[MISSING] {path}")
        # Auto-generate missing files except secrets
        if path.name == 'secrets.toml':
            print("Please create a secrets.toml manually with your Streamlit authentication secrets (for st.login).")
            print("See Streamlit docs: https://docs.streamlit.io/library/advanced-features/secrets-management")
            return False
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.suffix in ('.yaml', '.yml'):
                with open(path, 'w', encoding='utf-8') as f:
                    f.write('# Default configuration\n')
            elif path.suffix == '.csv':
                with open(path, 'w', encoding='utf-8') as f:
                    f.write('email,name,role,access,welcome_message\n')
            else:
                path.touch()
            print(f"[GENERATED] {path}")
            return True
        except Exception as e:
            print(f"[ERROR] Could not generate {path}: {e}")
            return False

def check_directory(path: Path) -> bool:
    if path.is_dir():
        print(f"[OK DIR] {path}")
        return True
    else:
        print(f"[MISSING DIR] {path}")
        # Auto-create missing directories
        try:
            path.mkdir(parents=True, exist_ok=True)
            print(f"[CREATED DIR] {path}")
            return True
        except Exception as e:
            print(f"[ERROR] Could not create directory {path}: {e}")
            return False

def main():
    # Parse user options for customizable paths
    parser = argparse.ArgumentParser(description="Setup Wizard for FonDeDeNaJa project.")
    parser.add_argument('--data-dir', default='data', help='Data directory')
    parser.add_argument('--img-dir', default='img', help='Image directory')
    parser.add_argument('--templates-dir', default='templates', help='Templates directory')
    parser.add_argument('--streamlit-dir', default='.streamlit', help='Streamlit directory')
    parser.add_argument('--app-dir', default='app', help='App directory')
    args = parser.parse_args()
    data_dir = Path(args.data_dir)
    img_dir = Path(args.img_dir)
    templates_dir = Path(args.templates_dir)
    streamlit_dir = Path(args.streamlit_dir)
    app_dir = Path(args.app_dir)

    required_dirs = [
        app_dir,
        app_dir / 'pages',
        data_dir,
        templates_dir,
        img_dir,
    ]
    required_files = [
        data_dir / 'settings.yaml',
        templates_dir / 'settings.yaml',
        streamlit_dir / 'secrets.toml',
        data_dir / 'user.csv',
    ]

    print(f"Using\n  data: {data_dir}\n  img: {img_dir}\n  templates: {templates_dir}\n  streamlit: {streamlit_dir}\n  app: {app_dir}\n")
    missing_items = False
    missing_entries = []  # Collect missing dirs/files for summary

    print("=== FonDeDeNaJa Setup Wizard ===\n")
    print("Checking required directories:")
    for d in required_dirs:
        if not check_directory(d):
            missing_items = True
            missing_entries.append(str(d))

    print("\nChecking required files:")
    for f in required_files:
        if not check_file(f):
            missing_items = True
            missing_entries.append(str(f))

    if missing_items:
        print("\nSome required files or directories are missing:")
        for item in missing_entries:
            print(f" - {item}")
        print("\nPlease create or restore the above items before continuing.")
        sys.exit(1)

    print("\nAll checks passed. Your environment looks good!")
    sys.exit(0)

if __name__ == "__main__":
    main()
