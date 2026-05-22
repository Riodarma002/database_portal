import streamlit as st
import base64
import os

# =========================================================================
# PERBAIKAN 1: Path gambar menggunakan os.path (relatif ke file ini)
#              → Tidak lagi hardcode path Windows "d:\File Kerja\..."
# PERBAIKAN 2: Kredensial login dibaca dari st.secrets
# =========================================================================

# Direktori tempat auth.py berada (digunakan untuk path relatif)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def add_login_css():
    img_path = os.path.join(BASE_DIR, ".streamlit", "bg_login.jpg")
    try:
        bin_str = get_base64_of_bin_file(img_path)
        bg_css = f"background-image: url('data:image/jpeg;base64,{bin_str}');"
    except:
        bg_css = "background-color: #f0f2f6;"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    /* Terapkan font hype modern ke seluruh elemen form */
    div[data-testid="stColumn"]:nth-child(2) * {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }}

    /* Full page background */
    .stApp {{
        {bg_css}
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    
    .main .block-container {{
        background: transparent !important;
    }}
    
    /* Solid White Card Style - Menggunakan :has() agar hanya menargetkan form login */
    div[data-testid="stColumn"]:has(#login-marker),
    div[data-testid="column"]:has(#login-marker) {{
        background: #FFFFFF !important;
        padding: 40px 40px !important;
        border-radius: 16px !important;
        border: none !important;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4) !important;
        margin-top: 5vh !important;
    }}
    
    /* MENCEGAH NESTED COLUMNS TERKENA STYLE KOTAK PUTIH */
    div[data-testid="stColumn"] div[data-testid="stColumn"],
    div[data-testid="column"] div[data-testid="column"] {{
        background: transparent !important;
        padding: 0 !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        margin-top: 0 !important;
    }}
    
    /* Text styles untuk Judul di dalam form */
    div[data-testid="stColumn"]:nth-child(2) h1,
    div[data-testid="column"]:nth-child(2) h1 {{
        color: #111 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        margin-top: 0 !important;
        font-weight: 800 !important;
        letter-spacing: -1px !important;
        text-shadow: none !important;
    }}
    
    /* Hide top header and sidebar */
    header[data-testid="stHeader"] {{
        display: none !important;
    }}
    section[data-testid="stSidebar"] {{
        display: none !important;
    }}
    
    /* Input field styling */
    div[data-testid="stTextInput"] input {{
        border-radius: 8px;
        border: 1px solid #ccc;
        background: #FFFFFF;
        padding: 12px 16px;
        font-size: 15px;
        color: #111;
        transition: all 0.2s ease;
    }}
    
    /* Change label color to bold black */
    .stTextInput label p {{
        color: #111 !important;
        font-weight: 700;
        font-size: 13.5px;
        margin-bottom: 5px;
        text-shadow: none;
    }}
    
    /* Input field focus - Thick black border */
    div[data-testid="stTextInput"] input:focus {{
        border-color: #000 !important;
        box-shadow: 0 0 0 1px #000 !important;
        background: #FFFFFF;
    }}

    /* Yellow Primary Button (Secure Login) */
    button[kind="primary"] {{
        background: #FFD33D !important;
        color: #111 !important;
        border-radius: 8px !important;
        padding: 8px 24px !important;
        border: none !important;
        box-shadow: none !important;
        font-weight: 700 !important;
        font-size: 15px !important;
    }}
    
    button[kind="primary"]:hover {{
        background: #F4C430 !important;
        color: #000 !important;
    }}

    /* White Secondary Button (Help?) */
    button[kind="secondary"] {{
        background: #FFFFFF !important;
        color: #111 !important;
        border-radius: 8px !important;
        padding: 8px 24px !important;
        border: 1px solid #111 !important;
        box-shadow: none !important;
        font-weight: 700 !important;
        font-size: 15px !important;
    }}
    
    button[kind="secondary"]:hover {{
        background: #f0f0f0 !important;
        color: #000 !important;
        border-color: #000 !important;
    }}
    
    /* Hilangkan teks 'Press Enter to apply' yang mengganggu */
    div[data-testid="InputInstructions"] {{
        display: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

def check_password():
    """Returns `True` jika user berhasil login."""

    # Render Logo
    logo_path = os.path.join(BASE_DIR, ".streamlit", "logo_mge.png")
    try:
        logo_base64 = get_base64_of_bin_file(logo_path)
        logo_html = f"<img src='data:image/png;base64,{logo_base64}' style='height: 55px; margin-bottom: 5px; object-fit: contain;'>"
    except:
        logo_html = ""

    # HTML gabungan untuk header agar simetris sempurna menggunakan flexbox
    header_html = f"""
    <div id='login-marker' class='login-wrapper' style='display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%;'>
        {logo_html}
        <div style='font-size: 2.2rem; font-weight: 800; color: #111; font-family: "Plus Jakarta Sans", sans-serif; letter-spacing: -1px; margin-top: 5px; text-align: center;'>
            Planning Portal Data
        </div>
        <div style='color: #666; font-size: 14.5px; margin-top: 8px; margin-bottom: 25px; text-align: center; line-height: 1.5; font-weight: 500;'>
            Centralized Data Synchronization System
        </div>
    </div>
    """

    def password_entered():
        """Cek username & password dari st.secrets."""
        valid_user = st.secrets["auth"]["username"]
        valid_pass = st.secrets["auth"]["password"]
        if st.session_state["username"] == valid_user and st.session_state["password"] == valid_pass:
            st.session_state["password_correct"] = True
            st.session_state["just_logged_in"] = True  # Flag untuk set cookie
            del st.session_state["password"]  # Jangan simpan password di session
        else:
            st.session_state["password_correct"] = False

    # 1. Cek Cookie Auto-Login sebelum memunculkan form
    if "password_correct" not in st.session_state:
        if hasattr(st, "context") and hasattr(st.context, "cookies"):
            # JANGAN auto-login jika user baru saja menekan tombol logout
            if st.context.cookies.get("auth_mge") == "logged_in" and not st.session_state.get("just_logged_out", False):
                st.session_state["password_correct"] = True

    if "password_correct" not in st.session_state:
        # Jika baru logout, hapus cookie via JS
        if st.session_state.get("just_logged_out", False):
            import streamlit.components.v1 as components
            js = """
            <script>
            document.cookie = "auth_mge=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
            </script>
            """
            components.html(js, height=0)
            st.session_state["just_logged_out"] = False

        add_login_css()
        
        # Dipersempit agar tidak terlalu lebar (1.5 di kiri dan kanan)
        col1, col2, col3 = st.columns([1.5, 1, 1.5])
        with col2:
            st.markdown(header_html, unsafe_allow_html=True)
            
            st.text_input("Username*", key="username", placeholder="Enter your username")
            st.text_input("Password*", type="password", key="password", placeholder="••••••••••")
            
            st.markdown("<p style='font-size: 12px; color: #666; margin-top: 15px; margin-bottom: 15px; line-height: 1.5;'>This information will be securely saved as per the <b>Terms of Service & Privacy Policy</b></p>", unsafe_allow_html=True)
            
            btn_col1, btn_col2 = st.columns([1, 2])
            with btn_col1:
                st.button("Help?", use_container_width=True)
            with btn_col2:
                st.button("Secure Login", on_click=password_entered, type="primary", use_container_width=True)
            
        return False
    
    elif not st.session_state["password_correct"]:
        add_login_css()
        
        col1, col2, col3 = st.columns([1.5, 1, 1.5])
        with col2:
            st.markdown(header_html, unsafe_allow_html=True)
            
            st.text_input("Username*", key="username", placeholder="Enter your username")
            st.text_input("Password*", type="password", key="password", placeholder="••••••••••")
            
            st.markdown("<p style='font-size: 12px; color: #666; margin-top: 15px; margin-bottom: 15px; line-height: 1.5;'>This information will be securely saved as per the <b>Terms of Service & Privacy Policy</b></p>", unsafe_allow_html=True)
            
            btn_col1, btn_col2 = st.columns([1, 2])
            with btn_col1:
                st.button("Help?", use_container_width=True)
            with btn_col2:
                st.button("Secure Login", on_click=password_entered, type="primary", use_container_width=True)
            
            st.error("⚠️ Username atau password salah.")
        return False
    else:
        # Jika baru login, set cookie 7 hari via JS
        if st.session_state.get("just_logged_in", False):
            import streamlit.components.v1 as components
            js = """
            <script>
            var d = new Date();
            d.setTime(d.getTime() + (7*24*60*60*1000));
            var expires = "expires="+ d.toUTCString();
            document.cookie = "auth_mge=logged_in;" + expires + ";path=/";
            </script>
            """
            components.html(js, height=0)
            st.session_state["just_logged_in"] = False
            
        return True

def logout():
    for key in ["password_correct", "username", "password"]:
        if key in st.session_state:
            del st.session_state[key]
            
    st.session_state["just_logged_out"] = True
    st.rerun()
