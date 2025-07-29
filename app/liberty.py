import streamlit as st
import pandas as pd
import toml
import os
import shutil
from dotenv import load_dotenv
from pathlib import Path
from colorama import Fore, Style, init as colorama_init
import streamlit.components.v1 as components
from appconfig import settings
from dataclasses import dataclass, field
colorama_init(autoreset=True)



def _browser_console_log(msg, level="log"):
    """
    Log a message to the browser's console using JavaScript via components.
    Level can be 'log', 'warn', or 'error'.
    """
    js = f"""
    <script>
    console.{level}({msg!r});
    </script>
    """
    components.html(js, height=0)
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


# Load main config using Config class
load_dotenv()
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


# Replace whoami class with cleaner dataclass-based implementation
@dataclass
class whoami:
    """
    User identity resolver.

    Resolves email (including devkey mode), loads user data, applies access rules,
    and builds a welcome message.

    Attributes:
        email (str): User's email address.
        DEV_MODE (bool): True if running in devkey mode.
        registered (bool): True if user is found in user.csv.
        name (str): The display name of the user.
        role (str): The assigned role.
        num_access (int): Numeric access level.
        access (str): String representation of access level.
        message (str): Welcome or status message.
    """
    email: str = None
    DEV_MODE: bool = False
    registered: bool = False
    name: str = "Unknown"
    role: str = "Guest"
    num_access: int = 0
    access: str = "Guest"
    message: str = field(default_factory=lambda: "Could not determine user.")

    def __post_init__(self):
        self.email = self._resolve_email(self.email)
        df = self._load_user_df()
        self._apply_access_rules(df)
        formats = {
            "name": self.name,
            "access": self.access,
            "email": self.email,
            "role": self.role,
            "num_access": self.num_access
        }
        self.message = self._build_message(df, formats)

    def _resolve_email(self, email):
        """Devkey logic, then fallback to st.user.email"""
        devkey_val = None
        try:
            devkey_val = st.query_params.get('devkey')
        except Exception:
            pass
        if settings.get("enable_devkey", False) and devkey_val == settings.get("dev_key", "L4D2"):
            # Devkey mode: skip st.user entirely
            email = "devkey@localhost"
            self.DEV_MODE = True
            print("Devkey mode: using safe defaults for user info.")
        else:
            print("No email provided in whoami function. Attempting st.user.email")
            SYSLOG("Dear developer : No email provided in whoami function. Attempting st.user.email", flag="WARN")
            try:
                email = st.user.email
            except Exception:
                SYSLOG("Fallback to st.user.email failed.\n> Double check your Streamlit authentication setup.\n> Double check your code to use user's email in whoami function.")
        return email

    def _load_user_df(self):
        """Load user.csv into DataFrame or alert/stop on missing file"""
        try:
            return pd.read_csv(os.path.join(os.getenv("DATA_DIR", "data"), "user.csv"), index_col="email")
        except FileNotFoundError:
            ALERT("User data file not found. Please ensure path to 'data/user.csv' exists.")
            st.stop()

    def _apply_access_rules(self, df):
        """Populate name, registered, role, num_access, access"""
        # Determine CSV-based registration only
        csv_registered = False
        if self.email is not None and self.email in df.index and not pd.isna(df.loc[self.email, "name"]):
            self.name = df.loc[self.email, "name"]
            csv_registered = True
        else:
            self.name = getattr(st.user, "name", "Unknown")
        self.registered = csv_registered

        self.role = df.loc[self.email, "role"] if "role" in df.columns and self.email in df.index else "User"
        if "access" in df.columns and self.email in df.index:
            access_val = df.loc[self.email, "access"]
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

    def _build_message(self, df, formats):
        """Format welcome_message or fallback to settings.msg_default"""
        default = settings.get("msg_default", "Welcome Back, {name} ({access})! Email = {email}").format(**formats)
        if "welcome_message" not in df.columns or self.email not in df.index:
            return default
        raw = df.loc[self.email, "welcome_message"]
        if not isinstance(raw, str) or pd.isna(raw) or not raw:
            return default
        try:
            return raw.format(**formats)
        except Exception:
            return default

    def __str__(self):
        return self.message
def sidebar(msg: str = None, user_obj: whoami = None):
    """
    Render the sidebar with user information and navigation options.

    Args:
        msg (str, optional): Additional message to display.
        user_obj (whoami, optional): Pre-instantiated user object. Defaults to None.
    """
    # Instantiate user if not provided
    if user_obj is None:
        try:
            user_obj = whoami(devkey=st.query_params.get('devkey'))
        except Exception:
            user_obj = whoami()
    st.sidebar.title("User Information")
    # Display the welcome message or user info
    st.sidebar.write(str(user_obj))

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
    access_level = getattr(user_obj, "num_access", None)
    if access_level is not None:
        try:
            user_access = int(access_level)
        except Exception:
            user_access = 0
        for page, min_access in page_access.items():
            if user_access >= min_access:
                nav_pages.append((page_titles.get(page, page), page))
    else:nav_pages.append(("Home", "main.py"))

    if nav_pages:
        _ = st.sidebar.selectbox("Navigate", [t for t, _ in nav_pages], key="sidebar_nav")
    else:
        st.sidebar.write("No pages available for your access level.")
    #In case addition messages need to be displayed
    if msg:
        st.sidebar.write(f"**Message:** {msg}")
def prevent_st_user_not_logged_in():
    """
    Prevents the app from running if the user is not logged in.
    """
    try:st.user.email
    except AttributeError:
        if st.button("Login", type="primary"):st.login()
        st.stop()
        SYSLOG("A user is not logged in. And trying to access the app.")
def accessible_pages():
    """
    Returns a dictionary of accessible pages based on user access level.
    """
    user = whoami()
    access_level = getattr(user, "num_access", None)
    if access_level is not None:
        try:
            user_access = int(access_level)
        except Exception:
            user_access = 0
    else:
        user_access = 0

    page_access = {
        "1_Entry.py": 1,
        "2_About_Me.py": 1,
        "3_Grader.py": 2,
    }
    accessible = {page: title for page, title in page_access.items() if user_access >= page_access[page]}
    return accessible
def padding():
    """
    Adds padding to the main content area of the Streamlit app.
    """
    st.markdown("""
            <style>
                .block-container {
                        padding-top: 2rem;
                        padding-bottom: 0rem;
                        padding-left: 5rem;
                        padding-right: 5rem;
                    }
            </style>
            """, unsafe_allow_html=True)
def mainload():
    """
    Main function to load the application.
    Doesn't accept any parameters.
    """
    from appconfig import settings
    from liberty import whoami, sidebar, prevent_st_user_not_logged_in, accessible_pages
    st.set_page_config(page_title="FonDeDeNaJa", page_icon="✏️", layout="wide")
    # Implement allowed permission page navigation in future
    check_secrets_file()
    prevent_st_user_not_logged_in()
    padding() #padding() function to add padding to the main content area (For making Zipher sane)
    # sidebar() removed to allow pages to control when/where sidebar renders
