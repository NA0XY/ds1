import streamlit as st
import pandas as pd
from db import initialize_database, create_event, get_all_events

def events_page():
    st.header("Events")

    # Initialize the database (safe to call multiple times)
    initialize_database()

    # Add Event Form
    with st.expander("Add New Event"):
        with st.form("add_event_form"):
            name = st.text_input("Event Name")
            description = st.text_area("Description")
            date = st.date_input("Event Date")
            location = st.text_input("Location")
            organizer_id = st.number_input("Organizer ID", min_value=1, step=1)
            submitted = st.form_submit_button("Add Event")
            if submitted:
                if name and description and location:
                    create_event(name, description, date, location, int(organizer_id))
                    st.success("Event added successfully.")
                else:
                    st.warning("Please fill in all required fields.")

    # Display All Events
    st.subheader("All Events")
    events = get_all_events()
    if events:
        df = pd.DataFrame(events)
        st.dataframe(df)
    else:
        st.info("No events found.")

# For Streamlit multipage support
if __name__ == "__main__":
    events_page()
