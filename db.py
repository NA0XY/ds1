import mysql.connector
from mysql.connector import Error
import streamlit as st

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'event_db',
    'user': 'root',
    'password': 'your_mysql_password'  # Update with your MySQL password
}

# Database connection
def create_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        st.error(f"Database connection error: {e}")
        return None

# Initialize database tables
def initialize_database():
    tables = [
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            role VARCHAR(50) DEFAULT 'user'
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS events (
            event_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            date DATE NOT NULL,
            location VARCHAR(100) NOT NULL,
            organizer_id INT NOT NULL,
            FOREIGN KEY (organizer_id) REFERENCES users(user_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            event_id INT NOT NULL,
            status ENUM('Pending', 'Confirmed', 'Cancelled') DEFAULT 'Pending',
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (event_id) REFERENCES events(event_id)
        )
        """
    ]
    
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            for table in tables:
                cursor.execute(table)
            conn.commit()
        except Error as e:
            st.error(f"Error initializing database: {e}")
        finally:
            cursor.close()
            conn.close()

# Event operations
def create_event(name, description, date, location, organizer_id):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO events (name, description, date, location, organizer_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, description, date, location, organizer_id))
            conn.commit()
            return cursor.lastrowid
        except Error as e:
            st.error(f"Error creating event: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

def get_all_events():
    conn = create_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM events")
            return cursor.fetchall()
        except Error as e:
            st.error(f"Error fetching events: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

# Booking operations
def create_booking(user_id, event_id):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO bookings (user_id, event_id)
                VALUES (%s, %s)
            """, (user_id, event_id))
            conn.commit()
            return cursor.lastrowid
        except Error as e:
            st.error(f"Error creating booking: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

def get_all_bookings():
    conn = create_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT b.booking_id, u.name AS user_name, e.name AS event_name, 
                       e.date, b.status
                FROM bookings b
                JOIN users u ON b.user_id = u.user_id
                JOIN events e ON b.event_id = e.event_id
            """)
            return cursor.fetchall()
        except Error as e:
            st.error(f"Error fetching bookings: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

# User operations (for future expansion)
def create_user(name, email, password, role='user'):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (name, email, password, role)
                VALUES (%s, %s, %s, %s)
            """, (name, email, password, role))
            conn.commit()
            return cursor.lastrowid
        except Error as e:
            st.error(f"Error creating user: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

def get_user_by_email(email):
    conn = create_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            return cursor.fetchone()
        except Error as e:
            st.error(f"Error fetching user: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
