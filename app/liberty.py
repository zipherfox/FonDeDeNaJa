import streamlit as st
import pandas as pd
import yaml
import toml
import os
import shutil
from dotenv import load_dotenv
from pathlib import Path
from colorama import Fore, Style, init as colorama_init
colorama_init(autoreset=True)

def _browser_console_log(msg, level="log"):
    """
    Log a message to the browser's console using JavaScript via st.markdown.
    Level can be 'log', 'warn', or 'error'.
    """
    js = f"""
    <script>
    console.{level}({msg!r});
    </script>
    """
    st.markdown(js, unsafe_allow_html=True)
def ALERT(msg: str,log: str=None):
    st.error(msg, icon="🚨")
    _browser_console_log(log if log else msg, level="error")
    if log is None:
        print(f"{Fore.RED}[ALERT]{Style.RESET_ALL} {msg}")
    else:
        print(f"{Fore.RED}[ALERT]{Style.RESET_ALL} {log}")


def WARN(msg: str, log: str = None):
    st.warning(msg, icon="⚠️")
    _browser_console_log(log if log else msg, level="warn")
    if log is None:
        print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} {msg}")
    else:
        print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} {log}")

def SYSLOG(log: str, flag: str = "LOG" ):
    """
    Log a message to the console. And show in browser console if possible.
    This is used for system-level logs that may not require user attention.
    Flag can be edited to indicate the type of log (e.g., "LOG", "ALERT", "WARNING").
    """
    if flag.capitalize() == "ALERT":
        print(f"{Fore.RED}[ALERT/System]{Style.RESET_ALL} {log}")
        _browser_console_log(log, level="error")
    elif flag.capitalize() == "WARNING" or flag.capitalize() == "WARN":
        print(f"{Fore.YELLOW}[WARNING/System]{Style.RESET_ALL} {log}")
        _browser_console_log(log, level="warn")
    else:
        print(f"{Fore.GREEN}[LOG/System]{Style.RESET_ALL} {log}")
        _browser_console_log(log, level="log")

def DEBUG(msg: str, DEV_MODE: bool = False, METHOD: str = None):
    if DEV_MODE:
        st.info(msg, icon="ℹ️")
        print(f"DEBUG: {msg}")
    else:
        st.toast("You don't have sufficient permissions to view this debug message.")
        print(f"DEBUG: {st.user.email} is trying to access a debug message without sufficient permissions.")

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
        if email is None:
            print("No email provided in whoami function. Attempting st.user.email")
            SYSLOG("Dear developer : No email provided in whoami function. Attempting st.user.email", flag="WARN")
            try:email = st.user.email
            except AttributeError:SYSLOG("Fallback to st.user.email failed.\n> Double check your Streamlit authentication setup.\n> Double check your code to use user's email in whoami function.")
        self.email = email
        self.name = "Unknown"
        self.role = "Guest"
        self.access = "Guest"
        self.message = "Could not determine user."
        st.session_state['email'] = email  # Store email in session state
        st.session_state['name'] = self.name
        st.session_state['role'] = self.role
        st.session_state['access'] = self.access
        self.DEVMODE = False  # Ensure DEVMODE attribute is always defined
        try:devkey = st.query_params["devkey"]
        except Exception:pass

        try:df = pd.read_csv(os.path.join(os.getenv("DATA_DIR", "data"), "user.csv"), index_col="email")
        except FileNotFoundError:
            ALERT("User data file not found. Please ensure path to 'data/user.csv' exists.")
            self.error = "User data file not found."
            st.stop()
            self.registered = False
            try:st.query_params.clear()
            except Exception:pass
        dev_key_config = config.get("devkey")
        if devkey and devkey == dev_key_config:
            DEBUG(f"User {st.session_state.get()} used developer key.")
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
            formats = {"name": self.name, "access": self.access, "email": self.email, "role": self.role, "num_access": self.num_access}
            if "welcome_message" in df.columns and email in df.index:
                raw_msg = df.loc[email, "welcome_message"].format(**formats)
            if pd.isna(raw_msg) or not raw_msg:
                self.message = config.get("msg_default", "Welcome {name} ({access})!").format(**formats)
            else:
                self.message = raw_msg.format(**formats)
                st.write("WARNING : DEVELOPER MODE ENABLED")
                st.toast("You are in Developer Mode")
    def __str__(self):
        return self.message
def sidebar(msg: str = None,user: str = None):
    """
    Render the sidebar with user information and navigation options.
    """
    st.sidebar.title("User Information")
    try:user = whoami(st.user.email)
    except Exception as e:user = user # Fallback to provided user if st.user.email is not available but user is provided in the function call
    if user is None:
        st.sidebar.warning("User information is not available. Please log in.")
        st.stop()
        return
    if user.registered:st.sidebar.write(user)
    else:
        st.sidebar.warning("You are not registered. Please contact the administrator.")

    if user.DEVMODE:
        st.sidebar.write(":[RED]Developer Mode is enabled.")

    # Navigation selectbox logic moved here
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
    access_level = getattr(user, "num_access", None)
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
        selected_page = st.sidebar.selectbox("Navigate", [t for t, _ in nav_pages], key="sidebar_nav")
        # Navigation logic should be handled externally using selected_page
    else:
        st.sidebar.write("No pages available for your access level.")
    #In case addition messages need to be displayed
    if msg:
        st.sidebar.write(f"**Message:** {msg}")
def prevent_st_user_not_logged_in():
    """
    Prevents the app from running if the user is not logged in.
    """
    try:st.user.is_logged_in
    except AttributeError:
        WARN("You are not logged in. Please log in to continue.",log="A user is not logged in. And trying to access the app.")
        if st.button("Login", type="primary"):st.login()
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
    user = whoami()
    
    # Render sidebar
    sidebar()
    