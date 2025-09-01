import toml
import os
from pathlib import Path
global template_settings_path
template_settings_path = Path(os.getenv("TEMPLATES_DIR", "templates")) / "data" / "settings.toml"
class settings:
    '''TOML configuration that is fine-tuned for FonDeDeNaJa.'''
    def __init__(self):
        settings_path = Path(os.getenv("SETTINGS_FILE", "data/settings.toml"))
        if not settings_path.is_file():
            # logger(f"Settings file not found at {settings_path}. Please ensure it exists.", flag="WARNING")
            self.settings = {}
        self.settings = toml.load(settings_path)
    def __getattr__(self, name):
        '''Get configuration value as an attribute.'''
        if name not in self.settings:
            # logger(f"'{self.__class__.__name__}' object has no attribute '{name}'", flag="ERROR")
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        return self.settings.get(name)
    def get(self, key, default=None):
        '''Get a configuration value by key, with an optional default.'''
        return self.settings.get(key, default)
    def set(self, key, value):
        '''Set a configuration value by key.'''
        self.settings[key] = value
        # Optionally save back to file
        settings_path = os.path.join(os.getenv("DATA_DIR", "data"), "settings.toml")
        with open(settings_path, 'w', encoding='utf-8') as f:
            toml.dump(self.settings, f)
    def __repr__(self):
        return f"<settings: {self.settings}>"
    def reset(self):
        '''Reset settings to default values. From template/settings.toml'''
        if not os.path.exists(template_settings_path):
            # logger(f"Template settings file not found at {template_settings_path}. Cannot reset settings.", flag="WARNING")
            return
        self.settings = toml.load(template_settings_path)
        # Save the reset settings back to the original file
        settings_path = os.path.join(os.getenv("DATA_DIR", "data"), "settings.toml")
        with open(settings_path, 'w', encoding='utf-8') as f:
            toml.dump(self.settings, f)
    def check(self):
        '''Check if all settings in templates are present in the current settings.'''
        template_settings = toml.load(template_settings_path)
        missing_settings = [key for key in template_settings if key not in self.settings]
        if missing_settings:
            # logger(f"Missing settings in current configuration: {missing_settings}", flag="WARNING")
            return False
        else:
            # logger("All template settings are present in the current configuration.", flag="LOG")
            return True
    def to_dict(self):
        '''Convert settings to a dictionary.'''
        return self.settings
if not os.getenv("ENV_LOADED"):
    # logger("Appconfig was called before environment variables were loaded.", flag="WARNING")
    pass

settings = settings()  # Create a global instance of settings
"""
Example usage
settings = settings()
print(settings.test_key)  # Access as attribute
print(settings.get("test_key"))  # Access using get method
settings.set("test_key", "This is a test")  # Set a new value
print(settings.get("test_key"))  # Should print This is a test
"""