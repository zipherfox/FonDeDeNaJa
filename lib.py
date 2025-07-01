def whoami(user_email):
    import pandas as pd
    devs = pd.read_csv("developers.csv")
    match = devs[devs['email'] == user_email]
    return "Kept you waiting huh? @" + match.iloc[0]['name'] if not match.empty else "You are logged in as: " + user_email
class sidebar:
    def __init__(self, DEVMODE=False):
        self.DEVMODE = DEVMODE
        import streamlit as st
        with st.sidebar:
            st.header("Your Info")
            if st.user.is_logged_in: st.write(whoami(st.user.email))
            elif self.DEVMODE:
                st.write("Developer Mode Enabled") 
                st.toast("You are in Developer Mode")
        pages = {
            "Navigation": [
                st.Page("main.py", title="Home"),
                st.Page("hello.py", title="Hello")
            ]
        }
        st.navigation(pages,position="sidebar")