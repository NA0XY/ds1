import mysql.connector
from mysql.connector import Error
import streamlit as st
import hashlib

DB_CONFIG = {
    'host': 'localhost',
    'database': 'event_mng',
    'user': 'root',
    'password': '19731973'  # Set your MySQL password
}

def create_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        st.error(f"Database connection error: {e}")
        return None

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def initialize_database():
    tables = [
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            role VARCHAR(20) DEFAULT 'user'
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
            active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (organizer_id) REFERENCES users(user_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            event_id INT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (event_id) REFERENCES events(event_id)
        )
        """
    ]
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            for table in tables:
                cursor.execute(table)
            cursor.close()

            cursor = conn.cursor(buffered=True)
            cursor.execute("SELECT * FROM users WHERE role='admin'")
            admin_exists = cursor.fetchone()
            if not admin_exists:
                cursor.execute(
                    "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                    ('Admin', 'admin@admin.com', hash_password('admin123'), 'admin')
                )
            conn.commit()
        except Error as e:
            st.error(f"Error initializing database: {e}")
        finally:
            cursor.close()
            conn.close()

def authenticate_user(email, password):
    conn = create_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s",
                           (email, hash_password(password)))
            return cursor.fetchone()
        except Error as e:
            st.error(f"Error authenticating user: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

def create_user(name, email, password, role='user'):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                (name, email, hash_password(password), role)
            )
            conn.commit()
            return cursor.lastrowid
        except Error as e:
            st.error(f"Error creating user: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

def create_event(name, description, date, location, organizer_id, active=True):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO events (name, description, date, location, organizer_id, active)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, description, date, location, organizer_id, active))
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
            cursor.execute("""
                SELECT e.*, u.name AS organizer_name FROM events e
                LEFT JOIN users u ON e.organizer_id = u.user_id
                ORDER BY e.event_id DESC
            """)
            return cursor.fetchall()
        except Error as e:
            st.error(f"Error fetching events: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

def set_event_active(event_id, active):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE events SET active = %s WHERE event_id = %s", (active, event_id))
            conn.commit()
        except Error as e:
            st.error(f"Error updating event: {e}")
        finally:
            cursor.close()
            conn.close()

def delete_event(event_id):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM events WHERE event_id = %s", (event_id,))
            conn.commit()
        except Error as e:
            st.error(f"Error deleting event: {e}")
        finally:
            cursor.close()
            conn.close()

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

def delete_booking(booking_id):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM bookings WHERE booking_id = %s", (booking_id,))
            conn.commit()
        except Error as e:
            st.error(f"Error deleting booking: {e}")
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
                       e.date, e.active, b.user_id, b.event_id
                FROM bookings b
                JOIN users u ON b.user_id = u.user_id
                JOIN events e ON b.event_id = e.event_id
                ORDER BY b.booking_id DESC
            """)
            return cursor.fetchall()
        except Error as e:
            st.error(f"Error fetching bookings: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
