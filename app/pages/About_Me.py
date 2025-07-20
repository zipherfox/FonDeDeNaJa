import streamlit as st
from liberty import mainload, whoami
st.title("User Information")
mainload()
if not st.user.is_logged_in:
    if st.button("Login", type="primary"):st.login()
else:
    user = whoami(st.user.email)
    if st.user.is_logged_in:st.image(st.user["picture"])
    if user.name == "Zipherfox":st.write(f":blue-background[**Name**] :blue[{user.name}] (:grey[{st.user['name']}])") 
    else:st.write(f":blue-background[**Name**] {user.name}")
    st.write(f":blue-background[**Email**] {user.email}")
    st.write(f":blue-background[**Role**] {user.role}")
    if user.access == "Unknown":st.write(f":blue-background[**Access Level**] :red[{user.access}]")
    elif user.access == "Superadmin":st.write(f":blue-background[**Access Level**] :rainbow[{user.access}]")
    else:st.write(f":blue-background[**Access Level**] {user.access}")
    st.write(f":blue-background[**Message**] {user.message}")
    if user.registered == True:
        st.write(":blue-background[**Registered**] :green[Yes]")
    else:
        st.write(":blue-background[**Registered**] :red[No]")
    if st.button("Logout"):
        st.logout()
        st.success("You have been logged out.")
        st.experimental_rerun()