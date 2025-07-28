import streamlit as st
from liberty import WARN, mainload, whoami
import pandas as pd
import os
st.title("Manage Permissions")
mainload()

@st.fragment
def editable_user_table(csv_path=os.getenv("USER_DATA_FILE", "data/user.csv")):
    df = pd.read_csv(csv_path)
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="user_edit_table")
    if st.button("Save Changes", type="primary"):
        # Backup old file
        backup_path = csv_path + ".bak"
        if whoami(st.user.email).num_access >= 4:
            st.info(f"[DEBUG] Saving to: {csv_path}")
        if os.path.exists(csv_path):
            os.replace(csv_path, backup_path)
        edited_df.to_csv(csv_path, index=False)
        st.success("User permissions updated and saved! Refreshing in 5 seconds...")
        import time
        for i in range(5, 0, -1):
            st.toast(f"Refreshing in {i} second{'s' if i > 1 else ''}...")
            time.sleep(1)
        st.rerun(scope="fragment")
        #For Developement purpose
        print(pd.read_csv(csv_path))
    return edited_df

if whoami().num_access < 4:st.write("You do not have sufficient permissions to manage user access levels.")
elif whoami().num_access >= 4:editable_user_table()
