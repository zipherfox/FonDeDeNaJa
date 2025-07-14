import importlib
import streamlit as st
import src.lib as lib
import datetime

class App:
    def __init__(self):
        pass
    def show(self):
        st.title("Welcome to the Application")
        # Display current date and time
        st.components.v1.html(
            '''
            <div id="today" style="font-size:22px; font-weight:bold; color:white;"></div>
            <div id="clock" style="font-size:20px; font-weight:normal; color:white;"></div>
            <script>
            function getOrdinal(n) {
                var s=["th","st","nd","rd"], v=n%100;
                return n+(s[(v-20)%10]||s[v]||s[0]);
            }
            function updateDateTime() {
                var now = new Date();
                var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
                var day = now.getDate();
                var month = months[now.getMonth()];
                var todayString = `Today : ${getOrdinal(day)} of ${month}`;
                var timeString = now.getHours().toString().padStart(2, '0') + ':' +
                    now.getMinutes().toString().padStart(2, '0') + ':' +
                    now.getSeconds().toString().padStart(2, '0');
                document.getElementById('today').innerHTML = todayString;
                document.getElementById('clock').innerHTML = 'Current time : ' + timeString;
            }
            setInterval(updateDateTime, 1000);
            updateDateTime();
            </script>
            ''',
            height=60,
        )
        # Display user information
        st.title("User Information")
        if not st.user.is_logged_in:
            if st.button("Login", type="primary"):st.login()
        else:
            user = lib.whoami(st.user.email)
            if st.user.is_logged_in:st.image(st.user["picture"])
            if user.name == "Zipherfox":st.write(f":blue-background[**Name**] :blue[{user.name}] (:grey[{st.user['name']}])") 
            else:st.write(f":blue-background[**Name**] {user.name}")
            st.write(f":blue-background[**Email**] {user.email}")
            st.write(f":blue-background[**Role**] {user.role}")
            if user.access == "Unknown":st.write(f":blue-background[**Access Level**] :red[{user.access}]")
            elif user.access == "Superadmin":st.write(f":blue-background[**Access Level**] :rainbow[{user.access}]")
            else:st.write(f":blue-background[**Access Level**] {user.access}")
            if st.button("Logout"):
                st.logout()
                st.success("You have been logged out.")
                st.experimental_rerun()

    def run(self, access_mode_level='Student'):
        if access_mode_level == 'Developer':
            lib.sidebar.DEVMODE = True
        else:
            lib.sidebar.DEVMODE = False
        lib.sidebar.DEVMODE = st.session_state.get('dev_mode', False)
        self.show()


if __name__ == "__main__":
    app = App()
    app.run()