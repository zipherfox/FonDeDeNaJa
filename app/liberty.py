import streamlit as st
import pandas as pd
import toml
import os

config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "config.toml")
config = toml.load(config_path)

def check_secrets_file():
    secrets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".streamlit", "secrets.toml")
    if os.path.isfile(secrets_path) == False:return WARN("secrets.toml file not found. Please create one in the .streamlit directory.")
    else:secrets_path = toml.load(secrets_path)
    if st.secrets["auth"] is None:return WARN("auth section not found in secrets.toml. Please add it.")
# Upon checking the secrets file, if st.user dictionary is still not available then something must've gone wrong with the streamlit's authentication system. 
    try:st.user.email
    except AttributeError:return WARN("Something went wrong with the user authentication dictionary. If you're seeing this message, please contact developers.")

# FYI whoami function returns a tuple of (access, name, role, msg) if the email is found in the developers.csv file. IT DOES NOT RETURN THE MESSAGE. ONLY VARIABLES!!!
def WARN(msg: str):  # Display a warning message in the Streamlit app and log on console too.
    st.warn(msg, icon="⚠️")
    print(f"WARNING: {msg}")


class whoami:
    def __init__(self, email: str = None, devkey: str = None):
        self.email = email
        self.name = "Unknown"
        self.role = "Guest"
        self.access = "Guest"
        self.msg = "Could not determine user."
        try:df = pd.read_csv("resources/user.csv", index_col="email")
        except FileNotFoundError:return WARN("User data file not found. Please ensure 'resources/user.csv' exists.")

        # Handle DevKey override
        if config.get("enable_devkey") and devkey == config.get("dev_key"):
            st.query_params.clear()  # Clear query params to prevent dev_key from being copied in the URL
            self.num_access = 69
            self.name = "DEVKEY ACCESS"
            self.role = "N/A"
            self.email = "N/A"
            self.message = "ONLY FOR DEVELOPMENT PURPOSES."
        # Determine name

        # If email is not found in the DataFrame, fallback to st.user and is not registered
        if pd.isna(df.loc[email, "name"]) or not df.loc[email, "name"]:
            self.name = st.user["name"]
            self.registered = False
        else:self.name = df.loc[email, "name"]

        # If there's no corresponding role to their email, assume they're just a User
        if "role" not in df.columns:self.role = "User"
        self.role = df.loc[email, "role"]
        # If access level is not found, assume it to be 1 (Student)
        if pd.isna(self.access) or not self.access:self.num_access = 1
        else:self.num_access = df.loc[email, "access"]
        # Map access names from numbers
        access_map = {1: "Student",2: "Teacher",3: "Admin",4: "Developer",5: "Superadmin",69: "DEVKEY ACCESS"}
        self.access = access_map.get(self.num_access, "Unknown")

        # Format message

        # If the message is not set or is NaN, use the default message from config
        raw_msg = df.loc[email, "welcome_message"]
        if pd.isna(raw_msg) or not raw_msg:
            self.message = config["msg_default"].format(name=self.name, access=self.access, email=self.email)
        else:self.message = raw_msg.format(name=self.name, access=self.access, email=self.email)
    # This function returns a string representation of the user information
    def __str__(self):
        return f"{self.name} ({self.access}) — {self.email}"

# This sidebar acts as a navigation bar for the Streamlit app, should be a part of the main layout.
class sidebar:
    def __init__(self, access_level=None):
        with st.sidebar:
            st.header("Your Info")
            # Display user information in the sidebar
            if st.user.is_logged_in:st.write(whoami(st.user.email))
            elif self.DEVMODE:
                st.write("WARNING : DEVELOPER MODE ENABLED")
                st.toast("You are in Developer Mode")
        # Define page access requirements as a dict: {page: min_access_level}
        self.access_level = access_level
        page_access = {
            "1_Entry.py": 1,  # Student
            "2_About_Me.py": 1,  # Student
            "3_Grader.py": 2,  
        }
        # Page titles as a dict
        page_titles = {
            "main.py": "Home",
            "hello.py": "Hello",
            "profile.py": "Profile",
            "admin.py": "Admin",
            "dev.py": "Developer",
            "superadmin.py": "Superadmin"
        }
        # Build navigation based on access level
        nav_pages = []
        if access_level is not None:
            try:
                user_access = int(access_level)
            except Exception:
                user_access = 0
            for page, min_access in page_access.items():
                if user_access >= min_access:
                    nav_pages.append(st.Page(page, title=page_titles.get(page, page)))
        else:
            nav_pages.append(st.Page("main.py", title="Home"))
        pages = {"Navigation": nav_pages}
        st.navigation(pages, position="sidebar")
def register(email):
    try:df = pd.read_csv("resources/user.csv", index_col="email")
    except FileNotFoundError:WARN("User data file not found. Please ensure 'resources/user.csv' exists.")
    check_secrets_file()
    if email not in df.index:
        st.warn("Your email is not registered.")
        print(email + " is not found in the database. Please adjust user.csv accordingly.")
