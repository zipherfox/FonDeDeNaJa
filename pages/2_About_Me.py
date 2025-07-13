import streamlit as st

st.title("About Me")
if st.user.is_logged_in:
    st.image(st.user.picture, width=120)
    st.markdown(f"**Name:** {st.user.name}")
    st.markdown(f"**Email:** {st.user.email}")
else:
    st.write("Please log in to view your profile.")
