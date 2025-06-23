import streamlit as st
def main():
    st.title("Welcome to My Streamlit App")
    st.write("This is a simple Streamlit application.")
    
    if st.button("Click Me"):
        st.write("Button clicked!")
    else:
        st.write("Button not clicked yet.")
if __name__ == "__main__":
    main()