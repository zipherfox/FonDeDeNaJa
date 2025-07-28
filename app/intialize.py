import os
from pathlib import Path
from dotenv import load_dotenv
import sys
from appconfig import settings
from image import DrawImage
image = DrawImage.from_url("https://content.imageresizer.com/images/memes/Side-eye-dog-meme-8.jpg",size=(80,40))

def check_env_requirements():
    load_dotenv()
    # Get required paths from environment or defaults
    data_dir = Path(os.getenv('DATA_DIR', 'data'))
    img_dir = Path(os.getenv('IMAGE_DIR', 'img'))
    templates_dir = Path(os.getenv('TEMPLATES_DIR', 'templates'))
    streamlit_dir = Path(os.getenv('STREAMLIT_DIR', '.streamlit'))
    app_dir = Path(os.getenv('APP_DIR', 'app'))
    required_dirs = [
        app_dir,
        app_dir / 'pages',
        data_dir,
        templates_dir,
        img_dir,
        streamlit_dir,
    ]
    required_files = [
        data_dir / 'settings.toml',
        streamlit_dir / 'secrets.toml',
        data_dir / 'user.csv',
    ]
    missing = []
    for d in required_dirs:
        if not d.exists() or not d.is_dir():
            missing.append(f"Missing directory: {d}")
    for f in required_files:
        if not f.exists() or not f.is_file():
            missing.append(f"Missing file: {f}")
    if missing:
        print("\nEnvironment check failed. The following are missing:")
        for m in missing:
            print(f" - {m}")
        print("\nPlease run the setup wizard or create the missing items before running the app.")
        sys.exit(1)
    print("✔️ Environment check passed. All required directories and files are present.")
    # All good
    return True
def check_config():
    if settings.check() == False:
        print("❌ Configuration check failed. Some required settings are missing.")
        sys.exit(1)
    # If we reach here, it means all required settings are present
    print("✔️ Configuration check passed. All required settings are present.")
    print("Using settings:")
    for key, value in settings.to_dict().items():
        print(f" - {key}: {value}")

if __name__ == "__main__":
    check_env_requirements()
    check_config()
