import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'event_db',
    'user': 'root',
    'password': 'your_mysql_password'  # <-- Change this to your actual MySQL password
}

# Database connection
def create_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None

# Initialize database tables
def initialize_db():
    commands = [
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100) UNIQUE,
            password VARCHAR(100),
            role VARCHAR(50)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS events (
            event_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            description TEXT,
            date DATE,
            location VARCHAR(100),
            organizer_id INT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            event_id INT,
            status VARCHAR(50)
        )
        """
    ]
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        for command in commands:
            cursor.execute(command)
        conn.commit()
        cursor.close()
        conn.close()

# CRUD Operations
def add_event(name, description, date, location, organizer_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO events (name, description, date, location, organizer_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, description, date, location, organizer_id))
            conn.commit()
            st.success("Event added successfully!")
        except Error as e:
            st.error(f"Error adding event: {e}")
        finally:
            cursor.close()
            conn.close()

def get_all_events():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM events")
            events = cursor.fetchall()
            return events
        except Error as e:
            st.error(f"Error fetching events: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

def add_booking(user_id, event_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO bookings (user_id, event_id, status)
                VALUES (%s, %s, 'Pending')
            """, (user_id, event_id))
            conn.commit()
            st.success("Booking request submitted!")
        except Error as e:
            st.error(f"Error creating booking: {e}")
        finally:
            cursor.close()
            conn.close()

def get_bookings():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT b.booking_id, u.name as user_name, e.name as event_name, b.status 
                FROM bookings b
                JOIN users u ON b.user_id = u.user_id
                JOIN events e ON b.event_id = e.event_id
            """)
            bookings = cursor.fetchall()
            return bookings
        except Error as e:
            st.error(f"Error fetching bookings: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

# Streamlit UI
def main():
    st.title("Event Management System")
    
    # Initialize database
    initialize_db()
    
    # Sidebar navigation
    menu = st.sidebar.selectbox("Menu", ["Home", "Add Event", "View Events", "Bookings"])
    
    if menu == "Home":
        st.subheader("Welcome to the Event Management System")
        st.write("Use the sidebar to navigate through the features of the application.")
        
    elif menu == "Add Event":
        st.subheader("Create New Event")
        with st.form("event_form"):
            name = st.text_input("Event Name")
            description = st.text_area("Description")
            date = st.date_input("Date")
            location = st.text_input("Location")
            organizer_id = st.number_input("Organizer ID", min_value=1)
            
            if st.form_submit_button("Add Event"):
                add_event(name, description, date, location, organizer_id)
                
    elif menu == "View Events":
        st.subheader("All Events")
        events = get_all_events()
        if events:
            df = pd.DataFrame(events)
            st.dataframe(df)
        else:
            st.info("No events found.")
            
    elif menu == "Bookings":
        st.subheader("Manage Bookings")
        
        # New booking form
        with st.expander("Create New Booking"):
            with st.form("booking_form"):
                user_id = st.number_input("User ID", min_value=1)
                event_id = st.number_input("Event ID", min_value=1)
                if st.form_submit_button("Submit Booking"):
                    add_booking(user_id, event_id)
        
        # Display bookings
        bookings = get_bookings()
        if bookings:
            df = pd.DataFrame(bookings)
            st.dataframe(df)
        else:
            st.info("No bookings found.")

if __name__ == "__main__":
    main()
