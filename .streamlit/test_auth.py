import streamlit as st
from streamlit_oauth import OAuth2Component
from streamlit_cookies_controller import CookieController

# Load secrets from secret.toml
client_id = st.secrets.client_id
client_secret = st.secrets.client_secret
redirect_uri = st.secrets.redirect_uri
server_metadata_url = st.secrets.server_metadata_url
cookie_secret = st.secrets.cookie_secret

oauth2 = OAuth2Component(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope="openid email profile",
    authorize_endpoint=None,
    token_endpoint=None,
    revoke_endpoint=None,
    server_metadata_url=server_metadata_url,
    cookie_secret=cookie_secret,
)

cookie_manager = CookieController()

result = oauth2.authorize_button("Login with Google")

if result and "userinfo" in result:
    user_email = result["userinfo"]["email"]
    # Set a secure cookie for the authenticated user
    cookie_manager.set("user_email", user_email, key=cookie_secret, expires_at=None, secure=True, httponly=True)
    st.write("Hello,", user_email)
else:
    st.write("Please log in with Google.")
