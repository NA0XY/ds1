import streamlit as st
from db import initialize_database, authenticate_user, create_user

# Initialize DB and session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

initialize_database()

def login():
    st.title("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = authenticate_user(email, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.success(f"Welcome, {user['name']}!")
            st.rerun()
        else:
            st.error("Invalid credentials.")

    st.markdown("---")
    st.write("Don't have an account? Register below.")
    with st.form("register_form"):
        reg_name = st.text_input("Name")
        reg_email = st.text_input("Register Email")
        reg_password = st.text_input("Register Password", type="password")
        submit = st.form_submit_button("Register")
        if submit:
            if reg_name and reg_email and reg_password:
                user_id = create_user(reg_name, reg_email, reg_password)
                if user_id:
                    st.success("Registration successful. Please log in.")
                    st.rerun()
            else:
                st.warning("Please fill in all fields.")

def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

def main_app():
    st.sidebar.title("Navigation")
    st.sidebar.write(f"Logged in as: {st.session_state.user['name']}")
    menu = ["Events", "Bookings"]
    if st.sidebar.button("Logout"):
        logout()
    choice = st.sidebar.radio("Go to", menu)
    if choice == "Events":
        from pages.Events import events_page
        events_page()
    elif choice == "Bookings":
        from pages.Bookings import bookings_page
        bookings_page()

def main():
    if st.session_state.logged_in:
        main_app()
    else:
        login()

if __name__ == "__main__":
    main()
