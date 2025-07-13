import streamlit as st

st.title("st.login Test")

if not st.user.is_logged_in:
    st.write("Please log in to see your user info.")
    st.login()
else:
    st.write("You are logged in!")
    st.write("st.user as dict:")
    st.json(dict(st.user))
