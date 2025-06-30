import streamlit as st
from streamlit_cookies_controller import CookieController

cookie_manager = CookieController()
cookie_secret = st.secrets.auth["cookie_secret"]
cookie = cookie_manager.get("user_email")
if cookie:
    # Refresh the cookie by resetting it (e.g., extend expiration by 1 day)
    import datetime
    expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    cookie_manager.set("user_email", cookie, key=cookie_secret, expires_at=expires_at, secure=True, httponly=True)
    st.write("Cookie refreshed for user:", cookie)
else:
    st.write("No user_email cookie found to refresh.")
print(cookie_manager.getAll())  # Debugging line to see all cookies