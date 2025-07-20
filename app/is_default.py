import os
from dotenv import load_dotenv
load_dotenv()

def is_file_default(file_path, default_path):
    """
    Checks if a file is unchanged from its default content.
    If default_path is provided and exists, compare file contents.
    If default_path does not exist, check if file is empty.
    """
    if not os.path.exists(file_path):
        return True
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    if default_path and os.path.exists(default_path):
        with open(default_path, 'r', encoding='utf-8') as fdef:
            default_content = fdef.read().strip()
        return content == default_content
    return content == ''

# Define file info in a dict for maintainability
FILES_INFO = {
    'answer_key.csv': {
        'env': 'ANSWER_KEY_FILE',
        'default': 'answer_key.csv',
    },
    'settings.yaml': {
        'env': 'SETTINGS_FILE',
        'default': 'settings.yaml',
    },
    'user.csv': {
        'env': 'USER_DATA_FILE',
        'default': 'user.csv',
    },
}

def is_default_state():
    """
    Returns a dict indicating if each key file is still default, using env paths.
    """
    data_dir = os.getenv('DATA_DIR', 'data')
    templates_dir = os.getenv('TEMPLATES_DIR', 'templates')
    results = {}
    for fname, info in FILES_INFO.items():
        data_path = os.getenv(info['env'], os.path.join(data_dir, info['default']))
        template_path = os.path.join(templates_dir, info['default'])
        results[fname] = is_file_default(data_path, template_path)
    return results

if __name__ == "__main__":
    print("Default state of key files:")
    for k, v in is_default_state().items():
        print(f"  {k}: {'default' if v else 'modified'}")