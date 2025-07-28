import streamlit as st
from liberty import whoami, mainload
mainload()
st.title("User Information")
user = whoami(devkey=st.query_params.get('devkey'))
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
    st.cache_resource.clear()
    st.experimental_rerun()