import streamlit as st
from app.liberty import WARN
import pandas as pd
import os

st.title("Manage Permissions")

def editable_user_table(csv_path="resources/user.csv"):
    df = pd.read_csv(csv_path)
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="user_edit_table")
    if st.button("Save Changes", type="primary"):
        # Backup old file
        backup_path = csv_path + ".bak"
        if os.path.exists(csv_path):
            os.replace(csv_path, backup_path)
        edited_df.to_csv(csv_path, index=False)
        st.success("User permissions updated and saved!")
        st.rerun()
    return edited_df

editable_user_table()
