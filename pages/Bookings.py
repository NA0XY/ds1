import streamlit as st
import pandas as pd
from db import create_booking, get_all_bookings, get_all_events

def bookings_page():
    user = st.session_state.user
    st.title("Bookings")

    if not user:
        st.warning("Please log in to view this page.")
        st.stop()

    # Show available events as a table for reference
    events = get_all_events()
    if events:
        df_events = pd.DataFrame(events)
        df_events['Active'] = df_events['active'].apply(lambda x: 'Yes' if x else 'No')
        st.write("Available Events:")
        st.dataframe(df_events[["event_id", "name", "date", "location", "Active"]])
    else:
        st.info("No events available for booking.")

    # Booking form (always visible)
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

    # Section to display all bookings
    st.subheader("All Bookings")
    bookings = get_all_bookings()
    if bookings:
        df = pd.DataFrame(bookings)
        df['Active'] = df['active'].apply(lambda x: 'Yes' if x else 'No')
        st.dataframe(df[["booking_id", "user_name", "event_name", "date", "Active"]])
    else:
        st.info("No bookings found.")

if __name__ == "__main__":
    bookings_page()
