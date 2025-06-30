import pandas as pd
# Easter Egg for developers
def whoami(user_email):
    devs = pd.read_csv("developers.csv")
    match = devs[devs['email'] == user_email]
    return "Kept you waiting huh? @" + match.iloc[0]['name'] if not match.empty else "You are logged in as: " + user_email