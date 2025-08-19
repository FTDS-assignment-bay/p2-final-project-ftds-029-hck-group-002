import streamlit as st
import pandas as pd
import os
import hashlib

# ===== Page Configuration =====
st.set_page_config(
    page_title="ScandidAI Login",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide sidebar completely
st.markdown("""
<style>
    [data-testid="collapsedControl"] {
        display: none;
    }
    section[data-testid="stSidebar"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ===== Custom CSS for UI =====
st.markdown("""
<style>
/* Background gradient */
.stApp {
    background: linear-gradient(135deg, #4f00bc, #29abe2);
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
}

/* Main container */
.main-container {
    width: 100%;
    max-width: 500px;
    padding: 20px;
}

/* Logo styling */
.app-logo {
    display: block;
    margin: 0 auto 15px auto;
    width: 50px;
    height: auto;
}

/* Title styling */
.login-title {
    text-align: center;
    margin-bottom: 25px;
    color: #333;
}

/* Input fields */
.stTextInput > div > div > input {
    background-color: black !important; /* kotak input jadi hitam */
    color: white !important; /* warna teks putih */
    border-radius: 8px;
    border: 1px solid #ced4da;
    padding: 10px 12px;
}

/* Placeholder text warna putih */
.stTextInput > div > div > input::placeholder {
    color: white !important;
    opacity: 0.8;
}

/* Label text input */
.stTextInput label {
    color: white !important;
    font-size: 130% !important;
    font-weight: 600;
}

/* Buttons */
.stButton > button {
    width: 100%;
    border-radius: 8px;
    font-weight: 600;
    padding: 10px;
    transition: all 0.3s ease;
}

/* Login button */
div[data-testid="column"]:nth-of-type(1) button {
    background: linear-gradient(to right, #00c6ff, #0072ff);
    color: white;
    border: none;
}

div[data-testid="column"]:nth-of-type(1) button:hover {
    background: linear-gradient(to right, #0072ff, #00c6ff);
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

/* Register button */
div[data-testid="column"]:nth-of-type(2) button {
    background: linear-gradient(to right, #ff512f, #dd2476);
    color: white;
    border: none;
}

div[data-testid="column"]:nth-of-type(2) button:hover {
    background: linear-gradient(to right, #dd2476, #ff512f);
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

/* Error messages */
.stAlert {
    border-radius: 8px;
}

/* Remove extra space */
[data-testid="stVerticalBlock"] > div:first-child {
    padding-top: 0;
}
</style>
""", unsafe_allow_html=True)

# ===== Helper Functions =====
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

# ===== User Data Storage =====
USER_FILE = "users.csv"

def init_user_file():
    if not os.path.exists(USER_FILE):
        pd.DataFrame(columns=["username", "password", "email"]).to_csv(USER_FILE, index=False)

def load_users():
    return pd.read_csv(USER_FILE)

def save_user(username, password, email):
    users_df = load_users()
    new_user = pd.DataFrame({
        "username": [username],
        "password": [hash_password(password)],
        "email": [email]
    })
    users_df = pd.concat([users_df, new_user], ignore_index=True)
    users_df.to_csv(USER_FILE, index=False)

# ===== Session State Initialization =====
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.current_page = "login"

# ===== Page Displays =====
def show_login_page():
    with st.container():
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        
        # Logo ScandidAI
        st.image("logo_scandidai.png", width=150, output_format="PNG", use_container_width=True)
        
        # Login Form
        username = st.text_input("Username", key="login_username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", use_container_width=True):
                users_df = load_users()
                if username in users_df["username"].values:
                    stored_password = users_df[users_df["username"] == username]["password"].values[0]
                    if verify_password(password, stored_password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.current_page = "dashboard"
                        st.rerun()
                    else:
                        st.error("Incorrect password!")
                else:
                    st.error("Username not found!")
        
        with col2:
            if st.button("Register", type="secondary", use_container_width=True):
                st.session_state.current_page = "register"
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

def show_register_page():
    with st.container():
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        
        st.image("logo_scandidai.png", width=50, output_format="PNG", use_container_width=True)
        st.markdown('<div class="login-title"><h2>🔑 Register</h2></div>', unsafe_allow_html=True)
        
        username = st.text_input("Username", key="reg_username", placeholder="Enter username")
        email = st.text_input("Email", key="reg_email", placeholder="Enter email")
        password = st.text_input("Password", type="password", key="reg_password", placeholder="Enter password")
        password_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm", placeholder="Re-enter password")
        
        if st.button("Sign Up", type="primary", use_container_width=True):
            if not username or not email or not password:
                st.error("All fields are required!")
            elif password != password_confirm:
                st.error("Passwords do not match!")
            else:
                users_df = load_users()
                if username in users_df["username"].values:
                    st.error("Username already exists!")
                else:
                    save_user(username, password, email)
                    st.success("Registration successful! Please log in.")
                    st.session_state.current_page = "login"
                    st.rerun()
        
        if st.button("Back to Login", use_container_width=True):
            st.session_state.current_page = "login"
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

def show_dashboard():
    st.title(f"👋 Welcome, {st.session_state.username}!")
    st.divider()
    
    st.subheader("Home")
    
    col1, col2, col3 = st.columns(3)
    
    container_style = """
    <style>
        .stContainer > div:first-child {
            height: 180px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
    </style>
    """
    st.markdown(container_style, unsafe_allow_html=True)
    
    with col1:
        with st.container(border=True):
            st.markdown("## Job List")
            st.write("List of available job vacancies")
            if st.button("Open", key="joblist_btn"):
                st.switch_page("pages/joblist.py")
    
    with col2:
        with st.container(border=True):
            st.markdown("## Apply Data Engineer")
            st.write("Submit your resume to the Data Engineer role")
            if st.button("Open", key="scandidai_de_btn"):
                st.switch_page("pages/scandidai_de.py")
    
    with col3:
        with st.container(border=True):
            st.markdown("## Apply Data Scientist")
            st.write("Submit your resume to the Data Scientist role")
            if st.button("Open", key="scandidai_ds_btn"):
                st.switch_page("pages/scandidai_ds.py")
    
    st.divider()
    if st.button("Logout", type="primary"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.current_page = "login"
        st.rerun()

# ===== Main App =====
def main():
    init_user_file()
    
    if not st.session_state.logged_in:
        if st.session_state.current_page == "login":
            show_login_page()
        else:
            show_register_page()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()
