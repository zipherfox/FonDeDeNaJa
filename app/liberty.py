import streamlit as st
import pandas as pd
import toml
import os
import shutil
from dotenv import load_dotenv
from pathlib import Path
from colorama import Fore, Style, init as colorama_init
import streamlit.components.v1 as components
from .config import settings
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


class whoami:
    def __init__(self, email: str = None, devkey: str = None):
        if email is None:
            devkey_val = None
            try:
                devkey_val = st.query_params.get('devkey')
            except Exception:
                pass
            if settings.get("enable_devkey", False) and devkey_val == settings.get("dev_key", "L4D2"):
                # Devkey mode: skip st.user entirely
                email = "devkey@localhost"
                self.DEVMODE = True
                print("Devkey mode: using safe defaults for user info.")
            else:
                print("No email provided in whoami function. Attempting st.user.email")
                SYSLOG("Dear developer : No email provided in whoami function. Attempting st.user.email", flag="WARN")
                try:
                    email = st.user.email
                except Exception:
                    SYSLOG("Fallback to st.user.email failed.\n> Double check your Streamlit authentication setup.\n> Double check your code to use user's email in whoami function.")
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
        try:
            devkey = st.query_params("devkey")
            SYSLOG(f"Detected devkey in query params is {devkey}", flag="DEBUG")
        except Exception:pass

        try:df = pd.read_csv(os.path.join(os.getenv("DATA_DIR", "data"), "user.csv"), index_col="email")
        except FileNotFoundError:
            ALERT("User data file not found. Please ensure path to 'data/user.csv' exists.")
            self.error = "User data file not found."
            st.stop()
            self.registered = False
            try:st.query_params.clear()
            except Exception:pass
        dev_key_config = settings.get("dev_key", "L4D2")
        if settings.get("enable_devkey", False) and devkey == dev_key_config:
            DEBUG(f"User {st.session_state.get()} used developer key.")
            self.name = getattr(st.user, "name", "Unknown") if hasattr(st, "user") else "Unknown"
            self.registered = False
            self.role = "N/A"
            self.access = "DEVKEY ACCESS"
            self.message = "ONLY FOR DEVELOPMENT PURPOSES."
            self.DEVMODE = True
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
                self.message = settings.get("msg_default", "Welcome Back, {name} ({access})! Email = {email}").format(**formats)
            else:
                self.message = raw_msg.format(**formats)
    def __str__(self):
        return self.message
def sidebar(msg: str = None,user: str = None):
    """
    Render the sidebar with user information and navigation options.
    """
    st.sidebar.title("User Information")
    st.sidebar.write(whoami())
    try:user = whoami(devkey=st.query_params('devkey'))
    except Exception as e:user = user # Fallback to provided user if st.user.email is not available but user is provided in the function call
    except AttributeError:
        pass  # If st.user is not available, we will use the provided user or None

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
    else:nav_pages.append(("Home", "main.py"))

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
        if st.button("Login", type="primary"):st.login()
        st.stop()
        SYSLOG("A user is not logged in. And trying to access the app.")
def mainload():
    """
    Main function to load the application.
    Doesn't accept any parameters.
    """
    import intialize
    from config import settings
    from liberty import whoami, sidebar, prevent_st_user_not_logged_in
    initialize_environment()
    check_secrets_file()
    prevent_st_user_not_logged_in()
    st.set_page_config(page_title="FonDeDeNaJa", page_icon="✏️", layout="wide")
    # Initialize user
    user = whoami()
    # Render sidebar
    sidebar()
    