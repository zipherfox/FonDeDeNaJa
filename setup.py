#!/usr/bin/env python3
"""Setup Wizard for FonDeDeNaJa project."""
import os
from dotenv import load_dotenv
import sys
import argparse
import shutil
from pathlib import Path
import random
import colorama
from colorama import Fore, Style

def gimmicks():
    lines = [
        "Asking docker if it can get your app to space",
        "Asking Fuji to receive Zipher's Steam gifts",
        "Bond, James Bond",
        "She sells sea shells by the shea sho DAMMIT!",
        "Why are you gay? -w- Does that make you gay???"
    ]
    return " - " + random.choice(lines) + " - "

def check_file(path: Path, generate: bool = True) -> bool:
    if path.exists():
        print(f"{Fore.GREEN}✔ [OK]{Style.RESET_ALL}     {path}")
        return True
    else:
        print(f"{Fore.YELLOW}✗ [MISSING]{Style.RESET_ALL} {path}")
        if not generate:
            return False
        # Auto-generate missing files except secrets
        if path.name == 'secrets.toml':
            print(f"{Fore.CYAN}Please create a secrets.toml manually with your Streamlit authentication secrets (for st.login).{Style.RESET_ALL}")
            print(f"See Streamlit docs: {Fore.BLUE}https://docs.streamlit.io/library/advanced-features/secrets-management{Style.RESET_ALL}")
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
            print(f"{Fore.GREEN}✔ [GENERATED]{Style.RESET_ALL} {path}")
            return True
        except Exception as e:
            print(f"{Fore.RED}✗ [ERROR]{Style.RESET_ALL} Could not generate {path}: {e}")
            return False

def check_directory(path: Path, generate: bool = True) -> bool:
    if path.is_dir():
        print(f"{Fore.GREEN}✔ [OK DIR]{Style.RESET_ALL}  {path}")
        return True
    else:
        print(f"{Fore.YELLOW}✗ [MISSING DIR]{Style.RESET_ALL} {path}")
        if not generate:
            return False
        # Auto-create missing directories
        try:
            path.mkdir(parents=True, exist_ok=True)
            print(f"{Fore.GREEN}✔ [CREATED DIR]{Style.RESET_ALL} {path}")
            return True
        except Exception as e:
            print(f"{Fore.RED}✗ [ERROR]{Style.RESET_ALL} Could not create directory {path}: {e}")
            return False

def main():
    # Load defaults from .env then parse user options for customizable paths
    mad = False
    load_dotenv()
    parser = argparse.ArgumentParser(description="Setup Wizard for FonDeDeNaJa project.")
    # Initialize colored output
    colorama.init(autoreset=True)
    parser.add_argument('--data-dir', default=os.getenv('DATA_DIR', 'data'),
                        help='Data directory')
    parser.add_argument('--img-dir', default=os.getenv('IMAGE_DIR', 'img'),
                        help='Image directory')
    parser.add_argument('--templates-dir', default=os.getenv('TEMPLATES_DIR', 'templates'),
                        help='Templates directory')
    parser.add_argument('--streamlit-dir', default=os.getenv('STREAMLIT_DIR', '.streamlit'),
                        help='Streamlit directory')
    parser.add_argument('--app-dir', default=os.getenv('APP_DIR', 'app'),
                        help='App directory')
    parser.add_argument('--no-gen', action='store_true', help='Do not auto-generate missing files or directories')
    args = parser.parse_args()
    # Interactive prompts for paths (press Enter to use the default)
    print("=== Interactive Setup ===\n(Leave blank and press Enter to use the default shown in [brackets])")
    val = input(f"Data directory [{args.data_dir}]: ").strip()
    data_dir = Path(val or args.data_dir).expanduser().resolve()
    val = input(f"Image directory [{args.img_dir}]: ").strip()
    img_dir = Path(val or args.img_dir).expanduser().resolve()
    val = input(f"Templates directory [{args.templates_dir}]: ").strip()
    templates_dir = Path(val or args.templates_dir).expanduser().resolve()
    val = input(f"Streamlit directory [{args.streamlit_dir}]: ").strip()
    streamlit_dir = Path(val or args.streamlit_dir).expanduser().resolve()
    val = input(f"App directory [{args.app_dir}]: ").strip()
    app_dir = Path(val or args.app_dir).expanduser().resolve()
    # Prompt for auto-generation of missing items, require explicit Y or N
    count = 0
    while True:
        gen_ans = input("Auto-generate missing files and directories? [Y/N]: ").strip().lower()
        if gen_ans in ('y', 'n'):
            break
        if gen_ans == '':
            print(f"{Fore.YELLOW}Please enter 'Y' or 'N'.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}I ASKED Y OR N GODDAMMIT. HOW IS IT SO HARD TO UNDERSTAND SUCH A SIMPLE INSTRUCTIONS!{Style.RESET_ALL}")
            mad = True
    gen_enabled = (gen_ans == 'y')

    required_dirs = [
        app_dir,
        app_dir / 'pages',
        data_dir,
        templates_dir,
        img_dir,
        streamlit_dir,  # Ensure Streamlit config dir exists
    ]
    required_files = [
        data_dir / 'settings.yaml',
        templates_dir / 'settings.yaml',
        streamlit_dir / 'secrets.toml',
        data_dir / 'user.csv',
    ]

    print("Using paths:")
    print(f" • data: {data_dir}")
    print(f" • img: {img_dir}")
    print(f" • templates: {templates_dir}")
    print(f" • streamlit: {streamlit_dir}")
    print(f" • app: {app_dir}\n")
    missing_items = False
    missing_entries = []  # Collect missing dirs/files for summary

    print("=== ✏️ FonDeDeNaJa Setup Wizard ✏️ ===\n")
    print("Checking required directories:")
    for d in required_dirs:
        if not check_directory(d, generate=gen_enabled):
            missing_items = True
            missing_entries.append(str(d))

    print("\nChecking required files:")
    for f in required_files:
        if not check_file(f, generate=gen_enabled):
            missing_items = True
            missing_entries.append(str(f))

    if missing_items:
        print("\nSome required files or directories are missing:")
        for item in missing_entries:
            print(f" - {item}")
        print("\nPlease create or restore the above items before continuing. :C")
        sys.exit(1)

    if not mad:
        print("\nAll checks passed. Your environment looks good! UwU\n" + gimmicks())
    else:
        print(f"\nAll checks passed. Jeez I'm not paid enough for this s***!")
    sys.exit(0)

if __name__ == "__main__":
    main()
