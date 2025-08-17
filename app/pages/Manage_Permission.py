import streamlit as st
from liberty import WARN, mainload, whoami, sidebar
import pandas as pd
import os
st.title("Manage Permissions")
@st.fragment
def editable_user_table(csv_path=os.path.join(os.getenv("DATA_DIR", "data"), "user.csv")):
    df = pd.read_csv(csv_path)
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="user_edit_table")
    if st.button("Save Changes", type="primary"):
        # Ensure user has permission
        user_obj = whoami()
        if user_obj.num_access < 4:
            st.error("Insufficient permissions to save changes.")
            return edited_df
        backup_path = f"{csv_path}.bak"
        try:
            if os.path.exists(csv_path):
                os.replace(csv_path, backup_path)
            edited_df.to_csv(csv_path, index=False)
        except Exception as e:
            st.error(f"Failed to save changes: {e}")
            return edited_df
        st.success("User permissions updated and saved!")
        import time
        with st.spinner("Refreshing user table..."):
            time.sleep(2)
        st.rerun(scope="fragment")
        # Development: print updated file
        print(pd.read_csv(csv_path))
    return edited_df

user_obj = whoami()
if user_obj.num_access < 4:
    st.write("You do not have sufficient permissions to manage user access levels.")
else:
    editable_user_table()
sidebar()