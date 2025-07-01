import streamlit as st
import lib
st.title("Hello Streamlit")
st.write("Hello, World!")
st.write("This is a simple Streamlit app to demonstrate the basic functionality.")
lib.sidebar(st.query_params["devkey"] == "L4D2")
