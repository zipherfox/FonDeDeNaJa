import streamlit as st
import whoami
import datetime
def main(): #Main application starts here
    st.title("Welcome to the Application")
    # Show dynamic current time using JavaScript
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
    # Show info in sidebar
    with st.sidebar:
        st.header("Your Info")
        st.write(whoami.whoami(st.user.email))
    # Add your application logic here
if st.user.is_logged_in == False:
    devkey = st.text_input("Enter Developer Key", type="password", on_change=None)
    if devkey:
        if devkey == "L4D2":
            st.success("Developer Key Accepted")
            main()
        else:
            st.error("Invalid Developer Key")
    if st.button("Login"):
        st.login()
elif st.user.is_logged_in == True:main()