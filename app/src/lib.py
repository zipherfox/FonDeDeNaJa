import streamlit as st
import pandas as pd
import toml
import os

config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".streamlit", "config.toml")
config = toml.load(config_path)


# Info : whoami function returns a tuple of (access, name, role, msg) if the email is found in the developers.csv file. IT DOES NOT RETURN THE MESSAGE. ONLY VARIABLES!!!
def warning(
    msg: str,
):  # Display a warning message in the Streamlit app and log on console too.
    st.warn(msg, icon="⚠️")
    print(f"WARNING: {msg}")


class whoami:
    def __init__(self, email: str = None, devkey: str = None):
        self.email = email
        self.name = "Unknown"
        self.role = "Guest"
        self.access = "Guest"
        self.msg = "Could not determine user."
        try:
            df = pd.read_csv("resources/user.csv", index_col="email")
        except FileNotFoundError:
            return st.error("User information not found. Is 'user.csv' present?")

        # Handle DevKey override
        if config.get("enable_devkey") and devkey == config.get("dev_key"):
            st.query_params.clear()  # Clear query params to prevent dev_key from being copied in the URL
            self.access = 4
            self.name = "DEVKEY ACCESS"
            self.role = "N/A"
            self.email = "N/A"
            self.message = "ONLY FOR DEVELOPMENT PURPOSES."
            return
        # Determine name
        if pd.isna(df.loc[email, "name"]) or not df.loc[email, "name"]:
            self.name = st.user["name"]
            self.registered = False
        else:
            self.name = df.loc[email, "name"]

        if "role" not in df.columns:
            self.role = "Guest"
        self.role = df.loc[email, "role"]

        # Map access level
        access_map = {
            1: "Student",
            2: "Teacher",
            3: "Admin",
            4: "Developer",
            5: "Superadmin",
        }
        self.access = access_map.get(df.loc[email, "access"], "Unknown")

        # Format message
        raw_msg = df.loc[email, "welcome_message"]
        if pd.isna(raw_msg) or not raw_msg:
            self.message = config["msg_default"].format(
                name=self.name, access=self.access, email=self.email
            )
        else:
            self.message = raw_msg.format(
                name=self.name, access=self.access, email=self.email
            )

    def __str__(self):
        return f"{self.name} ({self.access}) — {self.email}"


class sidebar:
    def __init__(self, DEVMODE=False):
        self.DEVMODE = DEVMODE
        with st.sidebar:
            st.header("Your Info")
            if st.user.is_logged_in:
                st.write(whoami(st.user.email))
            elif self.DEVMODE:
                st.write("WARNING : DEVELOPER MODE ENABLED")
                st.toast("You are in Developer Mode")
        pages = {
            "Navigation": [
                st.Page("main.py", title="Home"),
                st.Page("hello.py", title="Hello"),
            ]
        }
        st.navigation(pages, position="sidebar")
