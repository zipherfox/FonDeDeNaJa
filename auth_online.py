import streamlit as st
import pandas as pd

# Load secrets from secret.toml
# cookie_manager = CookieController()
# cookie_secret = st.secrets["cookie_secret"]

if st.user.is_logged_in:
    user_email = st.user.email if hasattr(st.user, 'email') else 'unknown'
    st.write("You are logged in as:", user_email)
    # Easter Egg for developers
    devs = pd.read_csv("developers.csv")
    match = devs[devs['email'] == user_email]
    if not match.empty:
        st.write(f"Kept you waiting huh? @{match.iloc[0]['name']}")
    else:
        st.write("You are logged in as :", user_email)
else:
    st.write("You are not logged in. Please log in to continue.")
    if st.button("Login"):st.login()
