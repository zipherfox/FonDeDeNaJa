"""Core application utilities for FonDeDeNaJa.

This module provides:
    * User identity resolution (`whoami`).
    * Sidebar / access helpers.
    * Simple system logging helpers (ALERT, WARN, SYSLOG, DEBUG).
    * Secrets / environment initialization utilities.
    * File-system indexing & organization utilities (`build_index`, `organize`).

Docstrings are written to optimize Pylance / IntelliSense hints.
"""
import streamlit as st
import pandas as pd
import toml, os, traceback
import shutil  # To manage files to respected folder
from pathlib import Path  # To build index
from dotenv import load_dotenv
from colorama import Back, Style, init as colorama_init  # For system logging purpose
import streamlit.components.v1 as components
from appconfig import settings
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Iterable, Mapping, Literal, Tuple
from logsetup import get_logger, inc_user_warning, inc_user_error
colorama_init(autoreset=True)

# Load main config using Config class
load_dotenv()
os.environ["ENV_LOADED"] = "TRUE" # Apparently .env is too dumb. It can't tell that TRUE/FALSE is boolean. 

def _browser_console_log(msg: str, level: str = "log") -> None:
    """Emit a message to the browser developer console.

    Parameters
    ----------
    msg : str
        The message to render.
    level : str, default 'log'
        One of 'log', 'warn', or 'error'.
    """
    js = f"""
    <script>
    console.{level}({msg!r});
    </script>
    """
    components.html(js, height=0)
def ALERT(msg: str, log: Optional[str] = None) -> None:
    """Display a critical error to the user and log it. FOR USER LEVEL

    Parameters
    ----------
    msg : str
        User-facing error message.
    log : str | None
        Alternate log text (if different from user-facing message).
    """
    st.error(msg, icon="🚨")
    _browser_console_log(log if log else msg, level="error")
    logger = get_logger()
    out = log if log else msg
    print(f"{Back.RED}[ALERT]{Style.RESET_ALL} {out}")
    logger.error(out)
    inc_user_error()


def WARN(msg: str, log: Optional[str] = None) -> None:
    """
    Display a non-fatal warning and log it. FOR USER LEVEL

    Parameters
    ----------
    msg : str
        User-facing warning message.
    log : str | None
        Alternate log text (if different from user-facing message).
    """
    st.warning(msg, icon="⚠️")
    _browser_console_log(log if log else msg, level="warn")
    logger = get_logger()
    out = log if log else msg
    print(f"{Back.YELLOW}[WARNING]{Style.RESET_ALL} {out}")
    logger.warning(out)
    inc_user_warning()

def DEBUG(msg: str, DEV_MODE: bool = False, METHOD: Optional[str] = None) -> None:
    """Conditionally show a debug message.

    Parameters
    ----------
    msg : str
        The debug information to surface.
    DEV_MODE : bool, default False
        If True, message is displayed; otherwise a permission toast appears.
    METHOD : str | None
        Optional hint of the originating method / context.
    """
    logger = get_logger()
    if DEV_MODE:
        st.info(msg, icon="ℹ️")
        print(f"DEBUG: {msg}")
        logger.debug(msg if METHOD is None else f"{METHOD}: {msg}")
    else:
        denied = f"{getattr(st.user, 'email', 'UNKNOWN_USER')} attempted to view debug output without permission."
        st.toast("You don't have sufficient permissions to view this debug message.")
        print(f"DEBUG: {denied}")
        logger.info(denied)

class SYSLOG:
    """
    An internal SYSTEM LOG that logs on system level with highlight color for better visibility
    Example:
    SYSLOG(f"User {st.user.email} logged in.",LOG)
    """
    def __init__(self,msg:str, flag: Literal["INFO", "WARNING", "ERROR"] = "INFO") -> None:
        self.msg = msg
        self.flag = flag
        if flag == "INFO":self.INFO(self.msg)
        elif flag == "WARNING":self.WARN(self.msg)
        elif flag == "ERROR":self.ERROR(self.msg)
    @staticmethod
    def INFO(msg:str) -> None:
        """Log an informational message."""
        print(f"{Back.GREEN}[SYSTEM/INFO]{Style.RESET_ALL} {msg}")
    @staticmethod
    def WARN(msg:str) -> None:
        """Log a warning message."""
        print(f"{Back.YELLOW}[SYSTEM/WARNING]{Style.RESET_ALL} {msg}")
    @staticmethod
    def ERROR(msg:str) -> None:
        """Log an error message."""
        print(f"{Back.RED}[SYSTEM/ERROR]{Style.RESET_ALL} {msg}")
        raise Exception("Critical Error flagged by developer")
"""Attach file logging to SYSLOG static methods without altering class definition."""
_app_logger = get_logger()
_orig_INFO = SYSLOG.INFO
_orig_WARN = SYSLOG.WARN
_orig_ERROR = SYSLOG.ERROR

def _info_proxy(msg: str):
    try:
        _orig_INFO(msg)
    finally:
        _app_logger.info(msg)

def _warn_proxy(msg: str):
    try:
        _orig_WARN(msg)
    finally:
        _app_logger.warning(msg)
    inc_user_warning()

def _error_proxy(msg: str):
    # Log first, then invoke original which raises
    _app_logger.error(msg)
    inc_user_error()
    _orig_ERROR(msg)

SYSLOG.INFO = staticmethod(_info_proxy)
SYSLOG.WARN = staticmethod(_warn_proxy)
SYSLOG.ERROR = staticmethod(_error_proxy)

def check_secrets_file() -> None:
    """Validate presence & structure of Streamlit `secrets.toml`.

    Warns in UI & console if file or required sections are missing.
    """
    secrets_path = Path(os.getenv("STREAMLIT_DIR", ".streamlit")) / "secrets.toml"
    if not secrets_path.is_file():
        return WARN("secrets.toml file not found. Please create one in the .streamlit directory.")
    try:
        secrets_data = toml.load(secrets_path)
        if "auth" not in secrets_data:
            return WARN("auth section not found in secrets.toml. Please add it.")
    except Exception as e:
        return WARN(f"Could not read secrets.toml: {e}")
def initialize_environment() -> None:
    """(Re)load environment variables from `.env` into process scope."""
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
    email: Optional[str] = None
    DEV_MODE: bool = False
    registered: bool = False
    name: str = "Unknown"
    role: str = "Guest"
    num_access: int = 0
    access: str = "Guest"
    message: str = field(default_factory=lambda: "Could not determine user.")

    def __post_init__(self) -> None:
        """Finalize initialization: resolve email, load CSV, build message."""
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
    def _resolve_email(self, email: Optional[str]) -> Optional[str]:
        """Resolve the active user email.

        Order of precedence:
            1. Devkey override (if enabled & matches key)
            2. Streamlit authenticated user (`st.user.email`)
        Returns a fallback `None` if neither available.
        """
        devkey_val = None
        try:
            devkey_val = st.query_params.get('devkey')
        except Exception:
            pass
        if settings.get("enable_devkey", False) and devkey_val == settings.get("dev_key"):
            email = "devkey@localhost"
            self.DEV_MODE = True
            print("Devkey mode: using safe defaults for user info.")
        else:
            print("No email provided in whoami function. Attempting st.user.email")
            SYSLOG.WARN("Dear developer : No email provided in whoami function. Attempting st.user.email")
            try:
                email = st.user.email
            except Exception:
                SYSLOG.WARN("Fallback to st.user.email failed.\n> Double check your Streamlit authentication setup.\n> Double check your code to use user's email in whoami function.")
        return email

    def _load_user_df(self) -> pd.DataFrame:
        """Load user.csv into DataFrame or alert/stop on missing file"""
        try:
            return pd.read_csv(os.path.join(os.getenv("DATA_DIR", "data"), "user.csv"), index_col="email")
        except FileNotFoundError:
            SYSLOG.WARN("User data file not found. Please ensure path to 'data/user.csv' exists.")
            st.stop()

    def _apply_access_rules(self, df: pd.DataFrame) -> None:
        """Populate role, access tier, registration flags from user DataFrame."""
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

    def _build_message(self, df: pd.DataFrame, formats: Mapping[str, Any]) -> str:
        """Produce a formatted welcome message (CSV override if valid)."""
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

    def __str__(self) -> str:
        return self.message
def sidebar(msg: Optional[str] = None, user_obj: Optional[whoami] = None) -> None:
    """Render sidebar with user info and navigation.

    Parameters
    ----------
    msg : str | None
        Optional extra message to display at bottom.
    user_obj : whoami | None
        Precomputed user object (saves re-loading CSV).
    """
    """
    Render the sidebar with user information and navigation options.

    Args:
        msg (str, optional): Additional message to display.
        user_obj (whoami, optional): Pre-instantiated user object. Defaults to None.
    """
    # Instantiate user if not provided
    if user_obj is None:
        # Removed unsupported devkey parameter during whoami() construction
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
def prevent_st_user_not_logged_in() -> None:
    """Enforce that a user session exists; offer login button if not."""
    """
    Prevents the app from running if the user is not logged in.
    """
    try:st.user.email
    except AttributeError:
        if st.button("Login", type="primary"):st.login()
        st.stop()
    SYSLOG("A user is not logged in. And trying to access the app.")
def accessible_pages() -> Dict[str, str]:
    """Return mapping of page filename -> title user can access."""
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

    page_access_levels: Dict[str, int] = {
        "1_Entry.py": 1,
        "2_About_Me.py": 1,
        "3_Grader.py": 2,
    }
    # Return mapping of page -> page (placeholder for future title mapping)
    return {page: page for page, min_level in page_access_levels.items() if user_access >= min_level}
def padding() -> None:
    """Inject global CSS padding adjustments into the current page."""
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
def mainload() -> None:
    """Perform one-time page setup (config, auth guard, layout padding)."""
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

IndexMap = Dict[Path, List[str]]


class build_index:
    """File-system index builder.

    Build an in-memory mapping of each directory under the data root to its
    immediate file children (non-recursive per directory entry). Designed for
    quick lookups without re-scanning disk every call.
    """

    def __init__(self, input: Optional[str] = None) -> None:
        base = input or os.getenv("DATA_DIR", "data")
        self.input: Path = Path(base).resolve()
        self.index: Optional[IndexMap] = None
        self.initial_status: Optional[str] = os.getenv("INDEX_BUILT")

    def initial(self) -> None:
        """Populate `self.index` with current recursive directory snapshot.

        Safe to call multiple times (overwrites prior snapshot). Sets the
        `INDEX_BUILT` environment variable to signal availability.
        """
        self.input = Path(os.getenv("DATA_DIR", "data")).resolve()
        # Build index only when called
        if not self.input.exists():
            ALERT(f"Path {self.input} does not exist.")
            return
        elif not self.input.is_dir():
            ALERT(f"Path {self.input} is not a directory.")
            return
        built: IndexMap = {}
        for subfolder in self.input.rglob("*"):
            if subfolder.is_dir():
                built[subfolder] = [str(f) for f in subfolder.iterdir() if f.is_file()]
        self.index = built
        SYSLOG(f"Index built for all subfolders in: {self.input}")
        os.environ["INDEX_BUILT"] = "True"
    #Make a predifined path for convenience in using build_index.preset()
    def refresh_scanned_csv(self) -> List[str]:
        """Return CSV file paths inside OCR output directory.

        Uses existing index if present; otherwise performs a direct scan.
        """
        ocr_dir = Path(os.getenv("OCR_OUTPUT_DIR", "./data/scanned_csv")).resolve()
        if self.index is None:
            if not ocr_dir.exists():
                return []
            return [str(p) for p in ocr_dir.rglob("*.csv") if p.is_file()]
        return [str(p) for p in self.index.keys() if p.suffix == ".csv"]
class organize:
    '''
    Organize files into subdirectories based on it's file name
    File format : <Subject ID>_<Student ID>_<read_count>
    <Subject ID>
    |-<Student ID>
    | |-<read_count>
    ...
    '''
    def __init__(self, input: Optional[str] = None) -> None:
        """Create an organizer instance.

        Parameters
        ----------
        input : str | None
            Root directory to organize (defaults to DATA_DIR env or 'data').
        """
        base = input or os.getenv("DATA_DIR", "data")
        self.input: Path = Path(base).resolve()
        self.index_builder = build_index(str(self.input))
        if os.getenv("INDEX_BUILT") != "True":
            self.index_builder.initial()
            SYSLOG.WARN("Organize was called before Index was built!")