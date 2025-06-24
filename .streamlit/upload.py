import streamlit as st
def file_IO():
    uploaded_file = st.file_uploader("Upload a ZIP file", type=["zip"], accept_multiple_files=False)
    if uploaded_file is not None:
        # Process the uploaded ZIP file
        st.write("File uploaded successfully!")
    elif uploaded_file is None:
        st.write("Please upload a file.")
    else:
        st.warning("Something went wrong with the upload.")
def drive_folder():
    if st.button("Select Folder from Google Drive"):
        st.write("Folder selected successfully!")