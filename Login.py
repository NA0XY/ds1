import streamlit as st
import pandas as pd
from db import (
    initialize_database, authenticate_user, create_user,
    create_event, get_all_events, set_event_active, delete_event,
    create_booking, get_all_bookings, delete_booking
)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

initialize_database()

def events_page():
    user = st.session_state.user
    st.title("Events")

    if not user:
        st.warning("Please log in to view this page.")
        st.stop()

    if user['role'] == 'admin':
        st.subheader("Add New Event")
        with st.form("add_event_form", clear_on_submit=True):
            name = st.text_input("Event Name")
            description = st.text_area("Description")
            date = st.date_input("Event Date")
            location = st.text_input("Location")
            organizer_id = user['user_id']
            active = st.selectbox("Is this event active?", ["Yes", "No"]) == "Yes"
            submit = st.form_submit_button("Add Event")
            if submit:
                if name and description and location:
                    create_event(name, description, date, location, organizer_id, active)
                    st.success("Event added successfully.")
                    st.rerun()
                else:
                    st.warning("Please fill in all required fields.")

        st.subheader("Set Event Active/Inactive and Delete")
        events = get_all_events()
        if events:
            df = pd.DataFrame(events)
            df['Active'] = df['active'].apply(lambda x: 'Yes' if x else 'No')
            st.dataframe(df[["event_id", "name", "date", "location", "Active"]])
            event_id = st.number_input("Enter Event ID to update active status or delete", min_value=1, step=1)
            new_status = st.selectbox("Set Active Status", ["Yes", "No"])
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Update Event Status"):
                    set_event_active(int(event_id), new_status == "Yes")
                    st.success("Event status updated.")
                    st.rerun()
            with col2:
                if st.button("Delete Event"):
                    delete_event(int(event_id))
                    st.success("Event deleted.")
                    st.rerun()
    else:
        st.info("Only admins can add, update, or delete events.")

    st.subheader("All Events")
    events = get_all_events()
    if events:
        df = pd.DataFrame(events)
        df['Active'] = df['active'].apply(lambda x: 'Yes' if x else 'No')
        st.dataframe(df[["event_id", "name", "date", "location", "Active"]])
    else:
        st.info("No events found.")

def bookings_page():
    user = st.session_state.user
    st.title("Bookings")

    if not user:
        st.warning("Please log in to view this page.")
        st.stop()

    events = get_all_events()
    if events:
        df_events = pd.DataFrame(events)
        df_events['Active'] = df_events['active'].apply(lambda x: 'Yes' if x else 'No')
        st.write("Available Events:")
        st.dataframe(df_events[["event_id", "name", "date", "location", "Active"]])
    else:
        st.info("No events available for booking.")

    st.subheader("Create New Booking")
    with st.form("create_booking_form", clear_on_submit=True):
        event_id = st.number_input("Enter Event ID to book", min_value=1, step=1)
        user_id = user['user_id']
        submit = st.form_submit_button("Book Event")

        if submit:
            if events:
                valid_event_ids = [e['event_id'] for e in events if e['active']]
                if int(event_id) in valid_event_ids:
                    create_booking(int(user_id), int(event_id))
                    st.success("Booking request submitted.")
                    st.rerun()
                else:
                    st.error("Invalid or inactive Event ID.")
            else:
                st.warning("No events to book.")

    st.subheader("All Bookings")
    bookings = get_all_bookings()
    if bookings:
        df = pd.DataFrame(bookings)
        df['Active'] = df['active'].apply(lambda x: 'Yes' if x else 'No')
        st.dataframe(df[["booking_id", "user_name", "event_name", "date", "Active"]])
        if user['role'] == 'admin':
            booking_id = st.number_input("Enter Booking ID to delete", min_value=1, step=1, key="delete_booking")
            if st.button("Delete Booking"):
                delete_booking(int(booking_id))
                st.success("Booking deleted.")
                st.rerun()
    else:
        st.info("No bookings found.")

def login():
    st.title("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = authenticate_user(email, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.success(f"Welcome, {user['name']} ({user['role']})!")
            st.rerun()
        else:
            st.error("Invalid credentials.")

    st.markdown("---")
    st.write("Don't have an account? Register below.")
    with st.form("register_form"):
        reg_name = st.text_input("Name")
        reg_email = st.text_input("Register Email")
        reg_password = st.text_input("Register Password", type="password")
        reg_role = st.selectbox("Role", ["user"])  # Only allow user registration
        submit = st.form_submit_button("Register")
        if submit:
            if reg_name and reg_email and reg_password:
                user_id = create_user(reg_name, reg_email, reg_password, reg_role)
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
    st.sidebar.write(f"Logged in as: {st.session_state.user['name']} ({st.session_state.user['role']})")
    menu = ["Events", "Bookings"]
    choice = st.sidebar.radio("Go to", menu)
    if st.sidebar.button("Logout"):
        logout()
    if choice == "Events":
        events_page()
    elif choice == "Bookings":
        bookings_page()

def main():
    if st.session_state.logged_in:
        main_app()
    else:
        login()

if __name__ == "__main__":
    main()
