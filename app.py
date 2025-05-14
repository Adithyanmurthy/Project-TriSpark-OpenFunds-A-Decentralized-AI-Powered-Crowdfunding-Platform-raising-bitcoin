import streamlit as st
import os
import hashlib
import sqlite3
import re
import sys
from pathlib import Path
import time

# Initialize session state for login status
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Function to initialize user authentication database
def init_auth_db():
    # Make sure db directory exists
    os.makedirs("db", exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect('db/users.db')
    c = conn.cursor()
    
    # Create table if it doesn't exist
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

# Initialize auth database
init_auth_db()

# Hash the password for security
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Validate email format
def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))

# User registration function
def register_user(name, email, password):
    conn = sqlite3.connect('db/users.db')
    c = conn.cursor()
    
    # Check if email already exists
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    if c.fetchone():
        conn.close()
        return False, "Email already registered"
    
    # Insert new user
    hashed_password = hash_password(password)
    c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", 
             (name, email, hashed_password))
    conn.commit()
    conn.close()
    return True, "Registration successful"

# User login function
def login_user(email, password):
    conn = sqlite3.connect('db/users.db')
    c = conn.cursor()
    
    # Find user by email
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    
    if user and user[3] == hash_password(password):
        return True, {"id": user[0], "name": user[1], "email": user[2]}
    return False, None

# Set page configuration
st.set_page_config(
    page_title="OpenFunds - Decentralized Fundraising App",
    page_icon="💰",
    layout="wide",
)

# Decide if sidebar should be shown
if not st.session_state.logged_in:
    # Add CSS to hide sidebar when not logged in
    st.markdown("""
    <style>
    /* Hide sidebar when not logged in */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Add custom CSS
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary: #7C4DFF;
        --secondary: #00E5FF;
        --background: #111122;
        --text: #FFFFFF;
        --accent: #FF4081;
        --success: #00E676;
        --warning: #FFAB40;
    }
    
    /* Global styling */
    .stApp {
        background: linear-gradient(135deg, #111122, #1A237E);
    }
    
    h1, h2, h3 {
        color: var(--text);
        font-weight: 600;
    }
    
    h1 {
        background: linear-gradient(90deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3em;
        margin-bottom: 0.5em;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, var(--primary), var(--secondary));
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.5em 2em;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(124, 77, 255, 0.4);
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-12oz5g7 {
        background: rgba(20, 20, 40, 0.7);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1A237E, #311B92);
    }
    
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stMetric label {
        color: var(--secondary);
    }
    
    /* Card containers */
    .dashboard-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .dashboard-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background-color: var(--primary);
        background-image: linear-gradient(90deg, var(--primary), var(--accent));
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        border: none;
    }
    
    .dataframe th {
        background-color: var(--primary);
        color: white;
    }
    
    /* Footer */
    footer {
        background: rgba(20, 20, 40, 0.5);
        padding: 1rem;
        border-radius: 10px;
        margin-top: 2rem;
    }
    
    /* Auth forms styling */
    .auth-container {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 2rem;
        max-width: 500px;
        margin: 0 auto;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }
    
    .auth-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .auth-form .stTextInput > div, 
    .auth-form div[data-baseweb="input"] {
        width: 100%;
    }
    
    .auth-form .stTextInput > label {
        color: var(--text);
    }
    
    .auth-form input {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        border-radius: 10px;
    }
    
    .auth-toggle {
        text-align: center;
        margin-top: 1rem;
        color: rgba(255, 255, 255, 0.7);
    }
    
    .auth-form .stButton > button {
        width: 100%;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

if 'auth_mode' not in st.session_state:
    st.session_state.auth_mode = 'login'

# Function to toggle between login and signup
def toggle_auth_mode():
    if st.session_state.auth_mode == 'login':
        st.session_state.auth_mode = 'signup'
    else:
        st.session_state.auth_mode = 'login'
    st.rerun()

# Function to show login/signup forms
def show_auth_page():
    # Logo and title
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, rgba(124, 77, 255, 0.2), rgba(0, 229, 255, 0.2)); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);">
            <div style="font-size: 4em; margin-bottom: 10px;">💰</div>
            <h2 style="background: linear-gradient(90deg, #7C4DFF, #00E5FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.2em; font-weight: 700; margin-bottom: 10px;">OpenFunds</h2>
            <p style="color: #FFFFFF; font-size: 1.2em; opacity: 0.8;">Decentralized Fundraising Platform</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Auth form container
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        
        if st.session_state.auth_mode == 'login':
            st.markdown('<div class="auth-header">', unsafe_allow_html=True)
            st.markdown('<h2>Log In to Your Account</h2>', unsafe_allow_html=True)
            st.markdown('<p style="color: rgba(255,255,255,0.7);">Welcome back to OpenFunds</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            with st.form("login_form"):
                st.markdown('<div class="auth-form">', unsafe_allow_html=True)
                email = st.text_input("Email Address")
                password = st.text_input("Password", type="password")
                
                submit_button = st.form_submit_button("Log In")
                
                if submit_button:
                    if not email or not password:
                        st.error("Email and password are required")
                    else:
                        success, user_info = login_user(email, password)
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.user_info = user_info
                            st.success(f"Welcome back, {user_info['name']}!")
                            st.rerun()
                        else:
                            st.error("Invalid email or password")
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="auth-toggle">', unsafe_allow_html=True)
            st.markdown('Need an account?')
            if st.button("Sign Up", key="auth_toggle_signup"):
                toggle_auth_mode()
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:  # Signup mode
            st.markdown('<div class="auth-header">', unsafe_allow_html=True)
            st.markdown('<h2>Create an Account</h2>', unsafe_allow_html=True)
            st.markdown('<p style="color: rgba(255,255,255,0.7);">Join the OpenFunds community</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            with st.form("signup_form"):
                st.markdown('<div class="auth-form">', unsafe_allow_html=True)
                name = st.text_input("Full Name")
                email = st.text_input("Email Address")
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                
                submit_button = st.form_submit_button("Sign Up")
                
                if submit_button:
                    if not name or not email or not password or not confirm_password:
                        st.error("All fields are required")
                    elif password != confirm_password:
                        st.error("Passwords do not match")
                    elif not is_valid_email(email):
                        st.error("Please enter a valid email address")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters long")
                    else:
                        success, message = register_user(name, email, password)
                        if success:
                            st.success(message)
                            st.session_state.auth_mode = 'login'
                            st.rerun()
                        else:
                            st.error(message)
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="auth-toggle">', unsafe_allow_html=True)
            st.markdown('Already have an account?')
            if st.button("Log In", key="auth_toggle_login"):
                toggle_auth_mode()
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display platform features below login form
    st.markdown("<h2 style='text-align: center; margin-top: 40px;'>Why Choose OpenFunds?</h2>", unsafe_allow_html=True)
    
    # Feature cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(124, 77, 255, 0.1); padding: 20px; border-radius: 15px; text-align: center; height: 100%;">
            <div style="font-size: 2em; margin-bottom: 10px;">🔒</div>
            <h4>Decentralized</h4>
            <p style="color: rgba(255,255,255,0.7);">No middlemen, all donations go directly to creators</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(0, 229, 255, 0.1); padding: 20px; border-radius: 15px; text-align: center; height: 100%;">
            <div style="font-size: 2em; margin-bottom: 10px;">👁️</div>
            <h4>Transparent</h4>
            <p style="color: rgba(255,255,255,0.7);">All campaigns and funding are publicly visible</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: rgba(255, 64, 129, 0.1); padding: 20px; border-radius: 15px; text-align: center; height: 100%;">
            <div style="font-size: 2em; margin-bottom: 10px;">🧠</div>
            <h4>AI-Powered</h4>
            <p style="color: rgba(255,255,255,0.7);">Smart suggestions and success predictions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="background: rgba(0, 230, 118, 0.1); padding: 20px; border-radius: 15px; text-align: center; height: 100%;">
            <div style="font-size: 2em; margin-bottom: 10px;">💸</div>
            <h4>No Fees</h4>
            <p style="color: rgba(255,255,255,0.7);">Keep 100% of what you raise, only pay network fees</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <footer style="margin-top: 60px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <p>© 2025 OpenFunds - A Decentralized Fundraising Platform</p>
            </div>
            <div style="display: flex; gap: 15px;">
                <span style="opacity: 0.7;">Follow us:</span>
                <a href="#" style="color: #00acee; text-decoration: none;">Twitter</a>
                <a href="#" style="color: #00acee; text-decoration: none;">Facebook</a>
                <a href="#" style="color: #00acee; text-decoration: none;">Instagram</a>
            </div>
        </div>
    </footer>
    """, unsafe_allow_html=True)

# Function to show the main app after login
def show_main_app():
    # Display home page content
    st.title("OpenFunds – Decentralized Fundraising App")

    # Logo section - using a modern gradient design
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, rgba(124, 77, 255, 0.2), rgba(0, 229, 255, 0.2)); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);">
            <div style="font-size: 4em; margin-bottom: 10px;">💰</div>
            <h2 style="background: linear-gradient(90deg, #7C4DFF, #00E5FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.2em; font-weight: 700; margin-bottom: 10px;">OpenFunds</h2>
            <p style="color: #FFFFFF; font-size: 1.2em; opacity: 0.8;">Decentralized Fundraising Platform</p>
        </div>
        """, unsafe_allow_html=True)

    # Welcome section with How It Works and Features
    st.write("## Welcome to OpenFunds!")
    st.write("OpenFunds is a modern decentralized fundraising platform that empowers creators and supporters to connect directly through blockchain technology.")

    st.write("### How It Works")

    # How It Works cards using separate markdown blocks to avoid HTML issues
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background: rgba(124, 77, 255, 0.1); padding: 20px; border-radius: 15px; text-align: center;">
            <div style="font-size: 2em; margin-bottom: 10px;"></div>
            <h4>Create</h4>
            <p>Set up your campaign with a compelling story and funding goal</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background: rgba(0, 229, 255, 0.1); padding: 20px; border-radius: 15px; text-align: center;">
            <div style="font-size: 2em; margin-bottom: 10px;"></div>
            <h4>Share</h4>
            <p>Share your campaign with friends, family, and supporters</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="background: rgba(255, 64, 129, 0.1); padding: 20px; border-radius: 15px; text-align: center;">
            <div style="font-size: 2em; margin-bottom: 10px;"></div>
            <h4>Fund</h4>
            <p>Accept Bitcoin donations directly to your wallet</p>
        </div>
        """, unsafe_allow_html=True)

    # Features list using native Streamlit components
    st.write("### Features")
    st.write("- **Decentralized** - No middlemen, donations go directly to creators")
    st.write("- **Transparent** - All campaigns and funding are publicly visible")
    st.write("- **Secure** - Built on blockchain technology for maximum security")
    st.write("- **Simple** - Easy to use interface with no technical knowledge required")

    # Footer
    st.markdown("""
    <footer>
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <p>© 2025 OpenFunds - A Decentralized Fundraising Platform</p>
            </div>
            <div style="display: flex; gap: 15px;">
                <span style="opacity: 0.7;">Follow us:</span>
                <a href="#" style="color: #00acee; text-decoration: none;">Twitter</a>
                <a href="#" style="color: #00acee; text-decoration: none;">Facebook</a>
                <a href="#" style="color: #00acee; text-decoration: none;">Instagram</a>
            </div>
        </div>
    </footer>
    """, unsafe_allow_html=True)

# Main layout: show different contents based on login state
if not st.session_state.logged_in:
    # If not logged in, show the auth page
    show_auth_page()
else:
    # When logged in, show sidebar
    st.sidebar.image("https://img.icons8.com/fluency/96/cryptocurrency.png", width=80)
    st.sidebar.markdown("<h3 style='text-align: center;'>OpenFunds</h3>", unsafe_allow_html=True)
    
    # Display user info
    if 'user_info' in st.session_state:
        st.sidebar.markdown(f"### Welcome, {st.session_state.user_info['name']}!")
    
    # Navigation using buttons
    st.sidebar.markdown("### Navigation")

    # Home button
    if st.sidebar.button("🏠 Home", key="home_nav", use_container_width=True):
        st.switch_page("pages/1_Home.py")

    # Create Campaign button
    if st.sidebar.button("➕ Create Campaign", key="create_nav", use_container_width=True):
        st.switch_page("pages/2_Create_Campaign.py")

    # View Campaigns button
    if st.sidebar.button("👁️ View Campaigns", key="view_nav", use_container_width=True):
        st.switch_page("pages/3_View_Campaigns.py")
    
    # Logout button
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", key="logout_btn", use_container_width=True):
        st.session_state.logged_in = False
        if 'user_info' in st.session_state:
            del st.session_state.user_info
        st.rerun()

    # Import some stats for the sidebar
    try:
        from models.campaign import Campaign
        import pandas as pd

        # Get statistics data
        campaigns = Campaign.get_all_campaigns()
        total_campaigns = len(campaigns) if campaigns else 0

        # Calculate total fundraising
        total_btc = 0
        if campaigns:
            for campaign in campaigns:
                total_btc += campaign['current_amount']

        # Display statistics
        st.sidebar.markdown("### Dashboard Stats")

        # Use Streamlit metrics instead of custom HTML for sidebar stats
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.sidebar.metric("Campaigns", f"{total_campaigns}")
            
        with col2:
            st.sidebar.metric("Total BTC", f"{total_btc:.4f}")
    except:
        st.sidebar.warning("Stats could not be loaded")
    
    # Show the main app content
    show_main_app()