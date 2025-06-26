import streamlit as st
import upload as up
# Upload zip or choose google drive folder function
def main():
    st.title("Welcome to My Streamlit App")
    st.login("Please log in to continue")
    st.write("This is a simple Streamlit application.")
    option = st.selectbox("Choose an option:", ["Upload ZIP", "Select Google Drive Folder"])
    match option:
        case "Upload ZIP":up.file_IO()
        case "Select Google Drive Folder":up.drive_folder()
    if st.button("Click Me"):st.write("Button clicked!")
    if st.button("Check secrets.toml"):st.write(st.secrets.test.message)
    else:st.write("Button not clicked yet.")
if __name__ == "__main__":
    main()
