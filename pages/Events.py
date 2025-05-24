import streamlit as st
import pandas as pd
from db import create_event, get_all_events, set_event_active

def events_page():
    user = st.session_state.user
    st.title("Events")

    if not user:
        st.warning("Please log in to view this page.")
        st.stop()

    # Only admins can add or deactivate events
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

        # Deactivate/reactivate events
        st.subheader("Set Event Active/Inactive")
        events = get_all_events()
        if events:
            df = pd.DataFrame(events)
            df['Active'] = df['active'].apply(lambda x: 'Yes' if x else 'No')
            st.dataframe(df[["event_id", "name", "date", "location", "Active"]])
            event_id = st.number_input("Enter Event ID to update active status", min_value=1, step=1)
            new_status = st.selectbox("Set Active Status", ["Yes", "No"])
            if st.button("Update Event Status"):
                set_event_active(int(event_id), new_status == "Yes")
                st.success("Event status updated.")
                st.rerun()
    else:
        st.info("Only admins can add or update events.")

    # Display all events
    st.subheader("All Events")
    events = get_all_events()
    if events:
        df = pd.DataFrame(events)
        df['Active'] = df['active'].apply(lambda x: 'Yes' if x else 'No')
        st.dataframe(df[["event_id", "name", "date", "location", "Active"]])
    else:
        st.info("No events found.")

if __name__ == "__main__":
    events_page()
