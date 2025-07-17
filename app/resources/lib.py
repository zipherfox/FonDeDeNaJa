import streamlit as st
import toml
config = toml.load(open("resources/config.toml", "r"))
# Info : whoami function returns a tuple of (access, name, role, msg) if the email is found in the developers.csv file. IT DOES NOT RETURN THE MESSAGE. ONLY VARIABLES!!!
def whoami(email,devkey=None):
    import pandas as pd
    try:df = pd.read_csv("resources/user.csv",index_col="email") # Preventing error if file not found
    except FileNotFoundError:return "User information not found, Is the file 'user.csv' present?"
    # Try st.user to prevent error if not logged in`
    if config["enable_devkey"] and devkey == config["dev_key"]:
        st.query_params.clear()  # Clear query params to prevent dev_key from being copied in the URL
        access = "DEV KEY"
        email = "N/A"
        name = "DEVKEY ACCESS"
        role = "UNKNOWN"
        msg = "PLEASE LOGIN PROPERLY USING OAUTH FOR SECURITY"
    if st.user.is_logged_in:
        if pd.isna(df.loc[email, 'name']) or not df.loc[email, 'name']:name = st.user["name"]
        else:name = st.user.name
    else:
        if pd.isna(df.loc[email, 'name']) or not df.loc[email, 'name']:name = st.user["name"]
        else:name = df.loc[email, 'name']
    role = df.loc[email, 'role']
    match df.loc[email, 'access']:
        case 1:access = "Student"
        case 2:access = "Teacher"
        case 3:access = "Admin"
        case 4:access = "Developer"
        case 5:access = "Superadmin"
    if pd.isna(df.loc[email, 'welcome_message']) or df.loc[email, 'welcome_message'] == '':
        msg = config["msg_default"].format(name=name, access=access, email=email)
    else: msg = df.loc[email, 'welcome_message'].format(name=name, access=access, email=email)
    info = tuple[access, name, role, msg, email]
    return msg
class sidebar:
    def __init__(self, DEVMODE=False):
        self.DEVMODE = DEVMODE
        with st.sidebar:
            st.header("Your Info")
            if st.user.is_logged_in: st.write(whoami(st.user.email))
            elif self.DEVMODE:
                st.write("WARNING : DEVELOPER MODE ENABLED")
                st.toast("You are in Developer Mode")
        pages = {"Navigation": [st.Page("main.py", title="Home"),st.Page("hello.py", title="Hello")]}
        st.navigation(pages,position="sidebar")
