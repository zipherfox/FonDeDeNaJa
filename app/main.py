import importlib
import env_check
import streamlit as st
import liberty as lib
import datetime

env_check.check_env_requirements()

class App:
    def __init__(self):
        pass
    def clock(self):
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

    def run(self, access_mode_level='Student'):
        if access_mode_level == 'Developer':lib.sidebar.DEVMODE = True
        else:lib.sidebar.DEVMODE = False
        lib.sidebar.DEVMODE = st.session_state.get('dev_mode', False)
        self.show()
    def show(self):
        st.title("Welcome to FonDeDeNaJa")
        st.write("This program is designed to validate the scores of bubble sheets. It is also capable of determining the access level of users based on their registered email addresses.")
if __name__ == "__main__":
    app = App()
    app.clock()
    lib.mainload()
    app.run()