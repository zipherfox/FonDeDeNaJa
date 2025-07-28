import streamlit as st
from liberty import mainload
st.title("Upload Page")
mainload()
st.write("Please upload your files here.")
uploaded_file = st.file_uploader("Choose a file", type=["jpg", "png", "jpeg"])
if uploaded_file is not None:
    st.write("Preview :")
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    st.success("File uploaded successfully!")