import streamlit as st
import pandas as pd
from db import initialize_database, create_booking, get_all_bookings

def main():
    st.title("Bookings")

    # Ensure the database and tables are initialized
    initialize_database()

    # Section to create a new booking
    with st.expander("Create New Booking"):
        with st.form("create_booking_form"):
            user_id = st.number_input("User ID", min_value=1, step=1)
            event_id = st.number_input("Event ID", min_value=1, step=1)
            submit = st.form_submit_button("Book Event")
            if submit:
                if user_id and event_id:
                    create_booking(int(user_id), int(event_id))
                    st.success("Booking request submitted.")
                else:
                    st.warning("Please provide both User ID and Event ID.")

    # Section to display all bookings
    st.subheader("All Bookings")
    bookings = get_all_bookings()
    if bookings:
        df = pd.DataFrame(bookings)
        st.dataframe(df)
    else:
        st.info("No bookings found.")

# For Streamlit multipage support
if __name__ == "__main__":
    main()
