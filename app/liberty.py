import streamlit as st
import pandas as pd
import yaml
import toml
import os
import shutil
from dotenv import load_dotenv
from pathlib import Path
def ALERT(msg: str):
    st.error(msg, icon="🚨")
    print(f"ALERT: {msg}")

def WARN(msg: str):
    st.warning(msg, icon="⚠️")
    print(f"WARNING: {msg}")

# Load main config
load_dotenv()
config_path = os.getenv("CONFIG_PATH", "data/settings.yaml")
data_path = os.getenv("CONFIG_DIR", "data")
try:
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    if not isinstance(config, dict):
        WARN("Config file is malformed or empty. Please check data/settings.yaml.")
        config = {}
except Exception as e:
    WARN(f"Could not load config file: {e}. Please check data/settings.yaml.")
    config = {}

def check_secrets_file():
    secrets_path = os.path.join(os.getenv("STREAMLIT_DIR", ".streamlit"), "secrets.toml")
    if not os.path.isfile(secrets_path):
        return WARN("secrets.toml file not found. Please create one in the .streamlit directory.")

    try:
        secrets_data = toml.load(secrets_path)
        if "auth" not in secrets_data:
            return WARN("auth section not found in secrets.toml. Please add it.")
    except Exception as e:
        return WARN(f"Could not read secrets.toml: {e}")

    try:
        if not hasattr(st, "user") or not hasattr(st.user, "email"):
            return WARN("User authentication information. Are you logged in?")
    except AttributeError:
        return WARN("User authentication information is missing. Please contact developers.")
def initialize_environment():
    load_dotenv()

class Config:
    def __init__(self):
        self.template_path = os.getenv("CONFIG_TEMPLATE", "templates/appconfig_template.yaml")
        self.user_path = os.getenv("CONFIG_PATH", "data/appconfig.yaml")
        self._config = None

    def _lazy_load(self):
        if self._config is None:
            self._ensure_config()

    def _load_yaml(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _save_yaml(self, path=None):
        if path is None:
            path = self.user_path
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self._config, f)

    def _merge(self, default: dict, user: dict) -> dict:
        for k, v in default.items():
            if k not in user:
                user[k] = v
            elif isinstance(v, dict) and isinstance(user[k], dict):
                self._merge(v, user[k])
        return user

    def _ensure_config(self):
        if not os.path.exists(self.user_path):
            os.makedirs(os.path.dirname(self.user_path), exist_ok=True)
            shutil.copy(self.template_path, self.user_path)

        default = self._load_yaml(self.template_path)
        user = self._load_yaml(self.user_path)
        self._config = self._merge(default, user)
        self._save_yaml()

    def save(self):
        self._lazy_load()
        self._save_yaml()

    def __getattr__(self, key):
        self._lazy_load()
        value = self._config.get(key)
        if value is None:
            raise AttributeError(f"Config has no attribute '{key}'")
        return value

    def __setattr__(self, key, value):
        if key.startswith("_") or key in {"template_path", "user_path"}:
            super().__setattr__(key, value)
        else:
            self._lazy_load()
            self._config[key] = value
            self._save_yaml()

    def to_dict(self):
        self._lazy_load()
        return self._config.copy()

class whoami:
    def __init__(self, email: str = None, devkey: str = None):
        self.email = email
        self.name = "Unknown"
        self.role = "Guest"
        self.access = "Guest"
        self.message = "Could not determine user."
        self.DEVMODE = False  # Ensure DEVMODE attribute is always defined

        try:
            df = pd.read_csv(os.path.join(os.getenv("DATA_DIR", "data"), "user.csv"), index_col="email")
        except FileNotFoundError:
            WARN("User data file not found. Please ensure 'resources/user.csv' exists.")
            self.error = "User data file not found."
            self.registered = False
            try:st.query_params.clear()
            except Exception:pass
        dev_key_config = config.get("dev_key")
        if devkey and devkey == dev_key_config:
            st.query_params.clear()
            self.name = getattr(st.user, "name", "Unknown") if hasattr(st, "user") else "Unknown"
            self.registered = False
            self.role = "N/A"
            self.access = "DEVKEY ACCESS"
            self.message = "ONLY FOR DEVELOPMENT PURPOSES."
        else:
            if email is None or email not in df.index or pd.isna(df.loc[email, "name"]):
                self.name = getattr(st.user, "name", "Unknown")
                self.registered = False
            else:
                self.name = df.loc[email, "name"]
                self.registered = True

            self.role = df.loc[email, "role"] if "role" in df.columns and email in df.index else "User"
            if "access" in df.columns and email in df.index:
                access_val = df.loc[email, "access"]
            else:
                access_val = None
            self.num_access = 1 if pd.isna(access_val) else int(access_val)

            access_map = {
                1: "Student",
                2: "Teacher",
                3: "Admin",
                4: "Developer",
                5: "Superadmin",
                69: "DEVKEY ACCESS"
            }
            self.access = access_map.get(self.num_access, "User")

            raw_msg = None
            if "welcome_message" in df.columns and email in df.index:
                raw_msg = df.loc[email, "welcome_message"]
            if pd.isna(raw_msg) or not raw_msg:
                self.message = config.get("msg_default", "Welcome {name} ({access})!").format(
                    name=self.name, access=self.access, email=self.email)
            else:
                self.message = raw_msg.format(name=self.name, access=self.access, email=self.email)
                st.write("WARNING : DEVELOPER MODE ENABLED")
                st.toast("You are in Developer Mode")
        page_access = {
            "1_Entry.py": 1,
            "2_About_Me.py": 1,
            "3_Grader.py": 2,
        }

        page_titles = {
            "main.py": "Home",
            "hello.py": "Hello",
            "profile.py": "Profile",
            "admin.py": "Admin",
            "dev.py": "Developer",
        }

        nav_pages = []
        access_level = getattr(self, "num_access", None)
        if access_level is not None:
            try:
                user_access = int(access_level)
            except Exception:
                user_access = 0
            for page, min_access in page_access.items():
                if user_access >= min_access:
                    nav_pages.append((page_titles.get(page, page), page))
        else:
            nav_pages.append(("Home", "main.py"))

        if nav_pages:
            selected_page = st.sidebar.selectbox("Navigate", [t for t, _ in nav_pages])
            # Navigation logic should be handled externally using selected_page
        else:
            st.sidebar.write("No pages available for your access level.")
def register(email):
    """
    Register a user by checking if their email exists in the user database.

    Parameters:
        email (str): The email address of the user to register.

    If the email is not found in 'resources/user.csv', a warning is displayed.
    """
    try:
        df = pd.read_csv(os.getenv("DATA_DIR", "data") + "/user.csv", index_col="email")
    except FileNotFoundError:
        return WARN("User database not found.")

    if email not in df.index:
        WARN("Your email is not registered.")
        print(f"{email} is not found in the database. Please adjust user.csv accordingly.")
def sidebar():
    """
    Render the sidebar with user information and navigation options.
    """
    st.sidebar.title("User Information")
    user = whoami(st.session_state.get('email', None), st.session_state.get('devkey', None))
    
    if user.registered:
        st.sidebar.write(f"**Name:** {user.name}")
        st.sidebar.write(f"**Role:** {user.role}")
        st.sidebar.write(f"**Access Level:** {user.access}")
        st.sidebar.write(f"**Email:** {user.email}")
        st.sidebar.write(f"**Message:** {user.message}")
    else:
        st.sidebar.warning("You are not registered. Please contact the administrator.")
    
    if user.DEVMODE:
        st.sidebar.write("Developer Mode is enabled.")
def prevent_st_user_not_logged_in():
    """
    Prevents the app from running if the user is not logged in.
    """
    try:
        st.user.is_logged_in
    except AttributeError:
        ALERT("User is not logged in. Please log in to continue.")
        if st.button("Login", type="primary"):st.login()
        st.stop()
def mainload():
    """
    Main function to load the application.
    """
    initialize_environment()
    check_secrets_file()
    prevent_st_user_not_logged_in()
    
    st.set_page_config(page_title="FonDeDeNaJa", page_icon=":guardsman:", layout="wide")
    
    # Load configuration
    config = Config()
    
    # Initialize user
    user = whoami(st.session_state.get('email', None), st.session_state.get('devkey', None))
    
    # Render sidebar
    sidebar()