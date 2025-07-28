from dynaconf import Dynaconf
import os
settings = Dynaconf(
    settings_files=[os.path.join(os.getenv("DATA_DIR", "config"), "settings.toml")],
)