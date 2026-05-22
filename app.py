import streamlit as st
import pandas as pd
import database
from auth import check_password, logout
import time
import os
from streamlit_option_menu import option_menu

# Direktori tempat app.py berada (digunakan untuk path relatif)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(page_title="MGE Portal", page_icon="🏢", layout="wide")

# =========================================================================
# GLOBAL CSS UNTUK SIDEBAR & UI
# =========================================================================
st.markdown("""
<style>
    /* Mengurangi ruang kosong (whitespace) di bagian paling atas aplikasi */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
    }

    /* Mempercantik dan mengecilkan ukuran header (judul) */
    h1 {
        color: #2E7D32 !important;
        font-weight: 800 !important;
        font-size: 2.0rem !important; /* Ukuran diperkecil */
        padding-top: 0rem !important;
        margin-top: -1rem !important; /* Ditarik ke atas */
        margin-bottom: 0.5rem !important;
    }
    
    /* Memperkecil elemen Filter (Input, Select, Button) */
    div[data-testid="stExpander"] input, 
    div[data-testid="stExpander"] div[data-baseweb="select"] > div {
        font-size: 13px !important;
        min-height: 32px !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }
    
    div[data-testid="stExpander"] button {
        padding: 2px 15px !important;
        font-size: 14px !important;
        min-height: 36px !important;
        border-radius: 6px !important;
    }
    
    div[data-testid="stExpander"] label {
        font-size: 13px !important;
        padding-bottom: 2px !important;
    }
    
    /* Modern Tab Navigation Styling */
    div[data-baseweb="tab-list"] {
        gap: 8px;
    }
    button[data-baseweb="tab"] {
        font-size: 15px !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        border-radius: 6px 6px 0 0 !important;
        transition: all 0.2s ease-in-out !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #1F4E78 !important;
        color: white !important;
    }
    button[data-baseweb="tab"][aria-selected="false"]:hover {
        background-color: #f0f2f6 !important;
        color: #1F4E78 !important;
    }
    
    /* Professional Sidebar Logout Button */
    div[data-testid="stSidebar"] div.stButton > button {
        border: 1.5px solid #d32f2f !important;
        color: #d32f2f !important;
        background-color: transparent !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease-in-out !important;
    }
    div[data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #d32f2f !important;
        color: white !important;
        border: 1.5px solid #d32f2f !important;
    }
</style>
""", unsafe_allow_html=True)

# Cek Login
if not check_password():
    st.stop()

# =========================================================================
# SIDEBAR MENU PUSAT
# =========================================================================
# Daftar Modul Tanpa Emoji (Digantikan oleh ikon Bootstrap di option_menu)
module_list = [
    "Dashboard Utama", 
    "Modul Coal Hauling", 
    "Modul Overburden (OB)", 
    "Modul MS Kontrak", 
    "Modul Fuel"
]

# Baca memori posisi menu dari URL (hanya saat pertama kali load)
if "active_menu_idx" not in st.session_state:
    active_module = st.query_params.get("module", "0")
    try:
        st.session_state["active_menu_idx"] = int(active_module)
        if st.session_state["active_menu_idx"] >= len(module_list):
            st.session_state["active_menu_idx"] = 0
    except:
        st.session_state["active_menu_idx"] = 0

with st.sidebar:
    import base64
    try:
        logo_path = os.path.join(BASE_DIR, ".streamlit", "logo_mge.png")
        with open(logo_path, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <div style="margin-bottom: 15px; display: flex; justify-content: center;">
                <img src="data:image/png;base64,{logo_b64}" style="height: 45px; object-fit: contain;">
            </div>
        """, unsafe_allow_html=True)
    except:
        pass
    st.markdown("<div style='margin-top: 15px;'>Selamat datang, <b>Admin Planning</b></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    menu = option_menu(
        menu_title=None,
        options=module_list,
        icons=["house-door", "truck", "cone-striped", "file-earmark-text", "fuel-pump"],
        menu_icon="cast",
        default_index=st.session_state["active_menu_idx"],
        key="sidebar_menu",
        styles={
            "container": {"padding": "0!important", "background-color": "transparent", "border": "none"},
            "icon": {"color": "#666", "font-size": "18px"}, 
            "nav-link": {
                "font-size": "14px", 
                "text-align": "left", 
                "margin":"0px", 
                "padding": "12px",
                "color": "#444",
                "font-weight": "500",
                "font-family": "'Plus Jakarta Sans', sans-serif"
            },
            "nav-link-selected": {
                "background-color": "#e0eaf5", 
                "color": "#1F4E78", 
                "font-weight": "700",
                "border-left": "4px solid #1F4E78",
                "border-radius": "0px"
            },
        }
    )
    
    # Simpan posisi menu ke session_state & query_params (tanpa rerun)
    try:
        current_idx = module_list.index(menu)
        st.session_state["active_menu_idx"] = current_idx
        st.query_params["module"] = str(current_idx)
    except:
        pass
        
    st.markdown("---")
    st.button(":material/logout: Logout", on_click=logout, use_container_width=True)


@st.cache_data(ttl=600)
def get_unique_vendors():
    df = database.fetch_data("SELECT DISTINCT vendor FROM coal_hauling WHERE vendor IS NOT NULL AND vendor != '' ORDER BY vendor")
    if not df.empty:
        return ["Semua"] + df['vendor'].tolist()
    return ["Semua"]

@st.cache_data(ttl=600)
def get_unique_unit_types():
    df = database.fetch_data("SELECT DISTINCT unit_type FROM coal_hauling WHERE unit_type IS NOT NULL AND unit_type != '' ORDER BY unit_type")
    if not df.empty:
        return ["Semua"] + df['unit_type'].tolist()
    return ["Semua"]

@st.cache_data(ttl=600)
def get_unique_pits():
    df = database.fetch_data("SELECT DISTINCT pit FROM coal_hauling WHERE pit IS NOT NULL AND pit != '' ORDER BY pit")
    if not df.empty:
        return ["Semua"] + df['pit'].tolist()
    return ["Semua"]

@st.cache_data(ttl=600)
def fetch_hauling_data(date_start=None, date_end=None):
    """Mengambil data hauling dari database. Di-cache berdasarkan rentang tanggal.
    Filter lainnya (shift, pit, vendor, dll) diterapkan client-side via Pandas."""
    query = """
    SELECT jml, day, date, shift, loading_date, voucher_number, pit, block, seam, product, concat, vendor, unit_type, unit_id, payload_arrival_time, payload_embark_time, weight_gross, weight_empty, weight_nett, destination, route, loader_id, tonage 
    FROM coal_hauling 
    WHERE 1=1
    """
    params = []
    
    if date_start and date_end:
        query += " AND date BETWEEN %s AND %s"
        params.extend([date_start, date_end])
    elif date_start:
        query += " AND date = %s"
        params.append(date_start)
    
    if date_start:
        query += " ORDER BY date DESC, id DESC"
    else:
        query += " ORDER BY date DESC, id DESC LIMIT 1000"
    
    return database.fetch_data(query, tuple(params) if params else None)

def clear_all_cache():
    """Menghapus semua cache data setelah operasi upload/delete."""
    fetch_hauling_data.clear()
    get_unique_vendors.clear()
    get_unique_unit_types.clear()
    get_unique_pits.clear()
    
    fetch_fuel_data.clear()
    get_unique_vendors_fuel.clear()
    get_unique_unit_types_fuel.clear()
    get_unique_locations_fuel.clear()
    
    get_dashboard_summary.clear()

@st.cache_data(ttl=600)
def get_dashboard_summary():
    last_hauling_str = "Belum Tersedia"
    last_fuel_str = "Belum Tersedia"
    hauling_yearly = pd.DataFrame()
    fuel_yearly = pd.DataFrame()
    hauling_daily = pd.DataFrame()
    fuel_daily = pd.DataFrame()

    try:
        df_hauling = database.fetch_data("SELECT MAX(date) as last_date FROM coal_hauling")
        if not df_hauling.empty and pd.notnull(df_hauling.iloc[0]['last_date']):
            last_hauling_str = df_hauling.iloc[0]['last_date'].strftime('%d %b %Y')
    except:
        pass

    try:
        df_fuel = database.fetch_data("SELECT MAX(date) as last_date FROM fuel")
        if not df_fuel.empty and pd.notnull(df_fuel.iloc[0]['last_date']):
            last_fuel_str = df_fuel.iloc[0]['last_date'].strftime('%d %b %Y')
    except:
        pass

    try:
        hauling_yearly = database.fetch_data("""
            SELECT DATE_FORMAT(date, '%Y-%m') as month, SUM(tonage) as total 
            FROM coal_hauling 
            GROUP BY month 
            ORDER BY month DESC LIMIT 12
        """)
        if not hauling_yearly.empty:
            hauling_yearly = hauling_yearly.sort_values('month')
    except:
        pass

    try:
        fuel_yearly = database.fetch_data("""
            SELECT DATE_FORMAT(date, '%Y-%m') as month, SUM(refueling) as total 
            FROM fuel 
            GROUP BY month 
            ORDER BY month DESC LIMIT 12
        """)
        if not fuel_yearly.empty:
            fuel_yearly = fuel_yearly.sort_values('month')
    except:
        pass

    try:
        hauling_daily = database.fetch_data("""
            SELECT date, SUM(tonage) as total 
            FROM coal_hauling 
            WHERE date >= (SELECT DATE_SUB(MAX(date), INTERVAL 30 DAY) FROM coal_hauling)
            GROUP BY date 
            ORDER BY date ASC
        """)
        if not hauling_daily.empty:
            hauling_daily['date'] = pd.to_datetime(hauling_daily['date']).dt.strftime('%d %b')
    except:
        pass

    try:
        fuel_daily = database.fetch_data("""
            SELECT date, SUM(refueling) as total 
            FROM fuel 
            WHERE date >= (SELECT DATE_SUB(MAX(date), INTERVAL 30 DAY) FROM fuel)
            GROUP BY date 
            ORDER BY date ASC
        """)
        if not fuel_daily.empty:
            fuel_daily['date'] = pd.to_datetime(fuel_daily['date']).dt.strftime('%d %b')
    except:
        pass

    return last_hauling_str, last_fuel_str, hauling_yearly, fuel_yearly, hauling_daily, fuel_daily


@st.cache_data(ttl=600)
def get_unique_vendors_fuel():
    df = database.fetch_data("SELECT DISTINCT vendor FROM fuel WHERE vendor IS NOT NULL AND vendor != '' ORDER BY vendor")
    if not df.empty:
        return ["Semua"] + df['vendor'].tolist()
    return ["Semua"]

@st.cache_data(ttl=600)
def get_unique_unit_types_fuel():
    df = database.fetch_data("SELECT DISTINCT unit_type FROM fuel WHERE unit_type IS NOT NULL AND unit_type != '' ORDER BY unit_type")
    if not df.empty:
        return ["Semua"] + df['unit_type'].tolist()
    return ["Semua"]

@st.cache_data(ttl=600)
def get_unique_locations_fuel():
    df = database.fetch_data("SELECT DISTINCT location FROM fuel WHERE location IS NOT NULL AND location != '' ORDER BY location")
    if not df.empty:
        return ["Semua"] + df['location'].tolist()
    return ["Semua"]

@st.cache_data(ttl=600)
def fetch_fuel_data(date_start=None, date_end=None):
    """Mengambil data fuel dari database. Di-cache berdasarkan rentang tanggal."""
    query = """
    SELECT id, unit_fix, date, periode, shift, time, reg_no, unit_code, unit_model, unit_type, brand, vendor, alocation, km, hm, fm_awal, fm_akhir, refueling, source, location, operator, fuelman, no_voucher
    FROM fuel 
    WHERE 1=1
    """
    params = []
    
    if date_start and date_end:
        query += " AND date BETWEEN %s AND %s"
        params.extend([date_start, date_end])
    elif date_start:
        query += " AND date = %s"
        params.append(date_start)
    
    if date_start:
        query += " ORDER BY date DESC, id DESC"
    else:
        query += " ORDER BY date DESC, id DESC LIMIT 1000"
    
    return database.fetch_data(query, tuple(params) if params else None)

# =========================================================================
# KONTEN BERDASARKAN MENU YANG DIPILIH
# =========================================================================

if menu == "Dashboard Utama":
    st.title("Dashboard Utama MGE")
    st.markdown("Ringkasan seluruh aktivitas operasional (Hauling, OB, MS, Fuel).")
    
    last_hauling_str, last_fuel_str, hauling_yearly, fuel_yearly, hauling_daily, fuel_daily = get_dashboard_summary()
    
    # Modern Metric Cards HTML
    st.markdown(f"""
    <style>
    .metric-card {{
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .metric-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }}
    .metric-icon {{
        font-size: 28px;
        margin-right: 15px;
        width: 60px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
    }}
    .icon-hauling {{ background-color: #e0f2fe; color: #0284c7; }}
    .icon-fuel {{ background-color: #fee2e2; color: #dc2626; }}
    .icon-ob {{ background-color: #fef3c7; color: #d97706; }}
    .icon-ms {{ background-color: #dcfce7; color: #16a34a; }}
    
    .metric-content {{ flex-grow: 1; }}
    .metric-title {{
        font-size: 13px;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    .metric-value {{
        font-size: 20px;
        font-weight: 700;
        color: #0f172a;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    </style>
    
    <div style="display: flex; gap: 15px; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 200px;" class="metric-card">
            <div class="metric-icon icon-hauling">🚛</div>
            <div class="metric-content">
                <div class="metric-title">Last Sync Hauling</div>
                <div class="metric-value">{last_hauling_str}</div>
            </div>
        </div>
        <div style="flex: 1; min-width: 200px;" class="metric-card">
            <div class="metric-icon icon-fuel">⛽</div>
            <div class="metric-content">
                <div class="metric-title">Last Sync Fuel</div>
                <div class="metric-value">{last_fuel_str}</div>
            </div>
        </div>
        <div style="flex: 1; min-width: 200px;" class="metric-card">
            <div class="metric-icon icon-ob">🚧</div>
            <div class="metric-content">
                <div class="metric-title">Last Sync OB</div>
                <div class="metric-value">Belum Tersedia</div>
            </div>
        </div>
        <div style="flex: 1; min-width: 200px;" class="metric-card">
            <div class="metric-icon icon-ms">📝</div>
            <div class="metric-content">
                <div class="metric-title">Last Sync MS</div>
                <div class="metric-value">Belum Tersedia</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🚛 Coal Hauling", "⛽ Fuel", "🚧 Overburden (OB)", "📝 MS Contract"])
    
    import plotly.express as px
    
    with tab1:
        st.subheader("Performance Coal Hauling")
        c1, c2 = st.columns(2)
        with c1:
            if not hauling_yearly.empty:
                fig1 = px.bar(hauling_yearly, x='month', y='total', title='Trend Tonase 12 Bulan Terakhir',
                              labels={'month': 'Bulan', 'total': 'Total Tonase (Ton)'},
                              text='total',
                              color_discrete_sequence=['#2563eb'])
                fig1.update_traces(
                    texttemplate='%{text:.2s}', 
                    textposition='outside', 
                    marker_line_width=0,
                    textfont=dict(size=11, color="#64748b"),
                    hovertemplate="<b>%{x}</b><br>Tonase: %{y:,.0f} Ton<extra></extra>"
                )
                fig1.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=20, r=20, t=50, b=20),
                    xaxis=dict(showgrid=False, title=""),
                    yaxis=dict(showgrid=True, gridcolor='#f1f5f9', title=""),
                    font=dict(family="Plus Jakarta Sans, sans-serif", color="#475569"),
                    title_font=dict(size=16, color="#0f172a", family="Plus Jakarta Sans, sans-serif")
                )
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.info("Data bulanan Coal Hauling belum tersedia.")
        
        with c2:
            if not hauling_daily.empty:
                fig2 = px.area(hauling_daily, x='date', y='total', title='Tonase Harian (30 Hari Terakhir)',
                               labels={'date': 'Tanggal', 'total': 'Tonase Harian (Ton)'},
                               color_discrete_sequence=['#10b981'])
                fig2.update_traces(
                    mode='lines+markers+text', 
                    text=hauling_daily['total'], 
                    texttemplate='%{text:.2s}', 
                    textposition='top center',
                    line_shape='spline',
                    fillcolor='rgba(16, 185, 129, 0.15)',
                    line=dict(width=3),
                    marker=dict(size=6, color='#10b981', line=dict(width=2, color='white')),
                    textfont=dict(size=10, color="#64748b"),
                    hovertemplate="<b>%{x}</b><br>Tonase: %{y:,.0f} Ton<extra></extra>"
                )
                fig2.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=20, r=20, t=50, b=20),
                    xaxis=dict(showgrid=False, title="", tickangle=-45),
                    yaxis=dict(showgrid=True, gridcolor='#f1f5f9', title=""),
                    font=dict(family="Plus Jakarta Sans, sans-serif", color="#475569"),
                    title_font=dict(size=16, color="#0f172a", family="Plus Jakarta Sans, sans-serif")
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Data harian Coal Hauling belum tersedia.")
                
    with tab2:
        st.subheader("Performance Fuel")
        c1, c2 = st.columns(2)
        with c1:
            if not fuel_yearly.empty:
                fig3 = px.line(fuel_yearly, x='month', y='total', title='Trend Konsumsi Fuel 12 Bulan Terakhir',
                               text='total',
                               labels={'month': 'Bulan', 'total': 'Total Fuel (Liter)'},
                               color_discrete_sequence=['#f43f5e'])
                fig3.update_traces(
                    mode='lines+markers+text',
                    texttemplate='%{text:.2s}', 
                    textposition='top center',
                    line_shape='spline',
                    line=dict(width=3),
                    marker=dict(size=7, color='#f43f5e', line=dict(width=2, color='white')),
                    textfont=dict(size=11, color="#64748b"),
                    hovertemplate="<b>%{x}</b><br>Fuel: %{y:,.0f} Liter<extra></extra>"
                )
                fig3.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=20, r=20, t=50, b=20),
                    xaxis=dict(showgrid=False, title=""),
                    yaxis=dict(showgrid=True, gridcolor='#f1f5f9', title=""),
                    font=dict(family="Plus Jakarta Sans, sans-serif", color="#475569"),
                    title_font=dict(size=16, color="#0f172a", family="Plus Jakarta Sans, sans-serif")
                )
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("Data bulanan Fuel belum tersedia.")
        
        with c2:
            if not fuel_daily.empty:
                fig4 = px.bar(fuel_daily, x='date', y='total', title='Konsumsi Fuel Harian (30 Hari Terakhir)',
                               text='total',
                               labels={'date': 'Tanggal', 'total': 'Konsumsi Harian (Liter)'},
                               color_discrete_sequence=['#f59e0b'])
                fig4.update_traces(
                    texttemplate='%{text:.2s}', 
                    textposition='outside', 
                    marker_line_width=0,
                    marker_color='rgba(245, 158, 11, 0.85)',
                    textfont=dict(size=10, color="#64748b"),
                    hovertemplate="<b>%{x}</b><br>Fuel: %{y:,.0f} Liter<extra></extra>"
                )
                fig4.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=20, r=20, t=50, b=20),
                    xaxis=dict(showgrid=False, title="", tickangle=-45),
                    yaxis=dict(showgrid=True, gridcolor='#f1f5f9', title=""),
                    font=dict(family="Plus Jakarta Sans, sans-serif", color="#475569"),
                    title_font=dict(size=16, color="#0f172a", family="Plus Jakarta Sans, sans-serif")
                )
                st.plotly_chart(fig4, use_container_width=True)
            else:
                st.info("Data harian Fuel belum tersedia.")
                
    with tab3:
        st.subheader("Performance Overburden (OB)")
        st.info("Placeholder untuk grafik Overburden. Data akan tampil jika modul ini sudah diisi.")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**(Placeholder) Trend BCM OB 12 Bulan Terakhir**")
            st.bar_chart({"Bulan": ["Jan", "Feb", "Mar"], "BCM": [0, 0, 0]}, x="Bulan", y="BCM")
        with c2:
            st.markdown("**(Placeholder) BCM Harian (30 Hari Terakhir)**")
            st.area_chart({"Tanggal": ["01", "02", "03"], "BCM": [0, 0, 0]}, x="Tanggal", y="BCM")
            
    with tab4:
        st.subheader("Performance Mine Survey (MS) Contract")
        st.info("Placeholder untuk grafik Mine Survey. Data akan tampil jika modul ini sudah diisi.")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**(Placeholder) Volume MS 12 Bulan Terakhir**")
            st.line_chart({"Bulan": ["Jan", "Feb", "Mar"], "Volume": [0, 0, 0]}, x="Bulan", y="Volume")
        with c2:
            st.markdown("**(Placeholder) Progress Volume (30 Hari Terakhir)**")
            st.bar_chart({"Tanggal": ["01", "02", "03"], "Volume": [0, 0, 0]}, x="Tanggal", y="Volume")


elif menu == "Modul Coal Hauling":
    st.title("Modul Coal Hauling")
    st.markdown("Sinkronisasi data produksi batubara (Coal Hauling).")
    
    tab1, tab2, tab3 = st.tabs([":material/monitoring: View Data", ":material/cloud_upload: Upload / Import", ":material/delete_sweep: Rollback / Delete Batch"])

    with tab1:
        
        with st.expander(":material/filter_alt: Filter & Cari Data", expanded=True):
            cols = st.columns([1.5, 0.9, 1, 1, 1, 1.2, 0.7, 0.5, 0.8])
            with cols[0]:
                f_date = st.date_input("Tanggal", value=[])
            with cols[1]:
                f_shift = st.selectbox("Shift", ["Semua", "DAY", "NIGHT"])
            with cols[2]:
                f_pit = st.selectbox("Pit", get_unique_pits())
            with cols[3]:
                f_vendor = st.selectbox("Vendor", get_unique_vendors())
            with cols[4]:
                f_unit = st.selectbox("Unit", get_unique_unit_types())
            with cols[5]:
                f_search = st.text_input("Pencarian", placeholder="Voucher/ID...")
            with cols[6]:
                st.markdown("<div style='margin-top:26px;'></div>", unsafe_allow_html=True)
                btn_search = st.button(":material/search: Cari", type="primary", use_container_width=True)
            with cols[7]:
                st.markdown("<div style='margin-top:26px;'></div>", unsafe_allow_html=True)
                if st.button(":material/refresh:", use_container_width=True, help="Tarik ulang data segar dari database"):
                    clear_all_cache()
                    st.rerun()
            with cols[8]:
                download_placeholder = st.container()

        # =====================================================================
        # OPTIMASI: SQL hanya dipanggil saat tanggal berubah (cached).
        # Filter Shift/Pit/Vendor/Unit/Search dikerjakan client-side via Pandas.
        # =====================================================================
        date_start = f_date[0] if len(f_date) >= 1 else None
        date_end = f_date[1] if len(f_date) >= 2 else None
        
        with st.spinner("Mengambil data..."):
            df = fetch_hauling_data(date_start, date_end)
        
        # Filter client-side (INSTAN, tanpa query SQL ulang)
        if not df.empty:
            if f_shift != "Semua":
                df = df[df['shift'] == f_shift]
            if f_pit != "Semua":
                df = df[df['pit'] == f_pit]
            if f_vendor != "Semua":
                df = df[df['vendor'] == f_vendor]
            if f_unit != "Semua":
                df = df[df['unit_type'] == f_unit]
            if f_search:
                mask = df['unit_id'].astype(str).str.contains(f_search, case=False, na=False) | \
                       df['voucher_number'].astype(str).str.contains(f_search, case=False, na=False)
                df = df[mask]
            
        if not df.empty:
            # Perbaiki format timedelta dari MySQL agar tampil sebagai HH:MM:SS
            for col in ['payload_arrival_time', 'payload_embark_time']:
                if col in df.columns:
                    df[col] = df[col].astype(str).apply(lambda x: x.split()[-1] if x != 'NaT' and x != 'None' else '')
            
            # Pastikan kolom berat adalah angka (float) agar bisa diformat dengan tepat
            for num_col in ['weight_gross', 'weight_empty', 'weight_nett', 'tonage']:
                if num_col in df.columns:
                    df[num_col] = pd.to_numeric(df[num_col], errors='coerce')
                    # Jika data ter-upload dalam format kg (ribuan), normalisasi kembali ke desimal ton
                    if num_col != 'tonage':
                        df[num_col] = df[num_col].apply(lambda x: x / 1000 if pd.notnull(x) and x >= 1000 else x)
                    
            # Pastikan kolom tanggal berformat datetime agar bisa diatur tampilannya
            for date_col in ['date', 'loading_date']:
                if date_col in df.columns:
                    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                    
            # -------------------------------------------------------------
            # Tombol Download Custom untuk memastikan format Excel sempurna
            # -------------------------------------------------------------
            df_export = df.copy()
            # Kunci 3 angka di belakang koma (tanpa pembulatan aneh dari Pandas)
            for col in ['weight_gross', 'weight_empty', 'weight_nett']:
                if col in df_export.columns:
                    df_export[col] = df_export[col].apply(lambda x: f"{float(x):.3f}" if pd.notnull(x) else "")
            # Kunci 2 angka di belakang koma untuk tonase
            if 'tonage' in df_export.columns:
                df_export['tonage'] = df_export['tonage'].apply(lambda x: f"{float(x):.2f}" if pd.notnull(x) else "")
            
            # Format tanggal juga dikembalikan ke format kalender normal
            for d_col in ['date', 'loading_date']:
                if d_col in df_export.columns:
                    df_export[d_col] = df_export[d_col].dt.strftime('%d/%m/%Y').fillna("")

            import io
            from openpyxl.styles import PatternFill, Font, Alignment
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_export.to_excel(writer, index=False, sheet_name='Data Hauling')
                
                # Mengambil worksheet untuk pewarnaan
                workbook = writer.book
                worksheet = writer.sheets['Data Hauling']
                
                # Mewarnai Header (Biru gelap dengan teks putih)
                header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
                header_font = Font(color="FFFFFF", bold=True)
                
                for cell in worksheet[1]:  # Baris 1 adalah header
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    
                # Proteksi Performa: Hanya lakukan styling/pewarnaan zebra jika data di bawah 2000 baris
                if len(df_export) <= 2000:
                    # Mewarnai baris selang-seling (Zebra striping - abu pucat)
                    gray_fill = PatternFill(start_color="F4F6F9", end_color="F4F6F9", fill_type="solid")
                    for row_idx in range(2, worksheet.max_row + 1):
                        if row_idx % 2 == 0:
                            for col_idx in range(1, worksheet.max_column + 1):
                                worksheet.cell(row=row_idx, column=col_idx).fill = gray_fill
                        
                    # Menyesuaikan lebar kolom secara otomatis
                    for col in worksheet.columns:
                        max_length = 0
                        column_letter = col[0].column_letter
                        for cell in col:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        worksheet.column_dimensions[column_letter].width = min(max_length + 2, 40) # Maksimal lebar 40

            excel_data = output.getvalue()
            
            # Menempatkan tombol download ke dalam placeholder di samping tombol Cari
            with download_placeholder:
                st.markdown("<div style='margin-top:26px;'></div>", unsafe_allow_html=True)
                st.download_button(
                    label=":material/download: Excel",
                    data=excel_data,
                    file_name=f"Report_Hauling_{time.strftime('%Y%m%d')}.xlsx",
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    use_container_width=True
                )
            
            # Ubah header menjadi kapital semua agar terlihat lebih tebal/bold
            col_cfg = {
                "weight_gross": st.column_config.NumberColumn("WEIGHT GROSS", format="%.3f"),
                "weight_empty": st.column_config.NumberColumn("WEIGHT EMPTY", format="%.3f"),
                "weight_nett": st.column_config.NumberColumn("WEIGHT NETT", format="%.3f"),
                "tonage": st.column_config.NumberColumn("TONAGE", format="%.2f"),
                "date": st.column_config.DateColumn("DATE", format="DD/MM/YYYY"),
                "loading_date": st.column_config.DateColumn("LOADING DATE", format="DD/MM/YYYY")
            }
            # Kapitalisasi sisa kolom lainnya
            for c in df.columns:
                if c not in col_cfg:
                    col_cfg[c] = st.column_config.Column(c.upper().replace('_', ' '))

            st.dataframe(
                df, 
                use_container_width=True, 
                hide_index=True, 
                height=700,
                column_config=col_cfg
            )
        else:
            st.info("Data hauling tidak ditemukan. Silakan ubah filter Anda.")

    with tab2:
        st.header("Update Data via Upload Excel")
        st.info("Pilih file `DAILY COAL HAULING MASTER REKAP.xlsx`")
        uploaded_file = st.file_uploader("Upload File Excel Hauling", type=["xlsx", "xlsb", "xls"], key="hauling")
        if uploaded_file is not None:
            if st.button(":material/cloud_upload: Import ke Server", type="primary"):
                with st.status("Memproses Import...", expanded=True) as status:
                    st.write("Membaca file Excel (Sheet: Timbangan)...")
                    try:
                        import numpy as np
                        # Header di baris ke-4 (index 3)
                        df_upload = pd.read_excel(uploaded_file, sheet_name='Timbangan', header=3)
                        
                        st.write("Menjalankan Auto-Validator...")
                        # 1. Bersihkan nama kolom (lowercase, konversi semua jenis spasi/newline/tab menjadi underscore)
                        df_upload.columns = df_upload.columns.astype(str).str.lower().str.strip().str.replace(r'\s+', '_', regex=True)
                        
                        # 2. Kolom database yang diharapkan
                        db_cols = ['jml', 'day', 'date', 'shift', 'loading_date', 'voucher_number', 'pit', 'block', 'seam', 'product', 'concat', 'vendor', 'unit_type', 'unit_id', 'payload_arrival_time', 'payload_embark_time', 'weight_gross', 'weight_empty', 'weight_nett', 'destination', 'route', 'loader_id', 'tonage']
                        
                        # 3. Filter hanya kolom yang relevan & buang baris kosong
                        available_cols = [c for c in db_cols if c in df_upload.columns]
                        df_insert = df_upload[available_cols].copy()
                        df_insert.dropna(subset=['voucher_number'], inplace=True)
                        
                        # 4. Format Tanggal YYYY-MM-DD
                        if 'date' in df_insert.columns:
                            df_insert['date'] = pd.to_datetime(df_insert['date'], errors='coerce').dt.strftime('%Y-%m-%d')
                        if 'loading_date' in df_insert.columns:
                            df_insert['loading_date'] = pd.to_datetime(df_insert['loading_date'], errors='coerce').dt.strftime('%Y-%m-%d')
                            
                        # 5. Parsing Time
                        for t_col in ['payload_arrival_time', 'payload_embark_time']:
                            if t_col in df_insert.columns:
                                df_insert[t_col] = df_insert[t_col].astype(str).apply(lambda x: x.split()[-1] if x not in ['NaT', 'nan', 'None'] else None)
                        
                        # 6. Bersihkan NaN menjadi None untuk MySQL
                        df_insert = df_insert.replace({np.nan: None, pd.NaT: None, 'nan': None})
                        
                        st.write(f"Mempersiapkan {len(df_insert)} baris untuk diimport...")
                        
                        # 7. Eksekusi Batch INSERT IGNORE
                        placeholders = ", ".join(["%s"] * len(available_cols))
                        cols_str = ", ".join(available_cols)
                        query_insert = f"INSERT IGNORE INTO coal_hauling ({cols_str}) VALUES ({placeholders})"
                        
                        data_to_insert = [tuple(x) for x in df_insert.to_numpy()]
                        
                        st.write("Mengimport batch data ke MySQL...")
                        success = database.execute_many_query(query_insert, data_to_insert)
                        
                        if success:
                            status.update(label="Import Selesai!", state="complete", expanded=False)
                            st.success(f"{len(df_insert)} Data Hauling berhasil diproses (duplikat diabaikan)!")
                            clear_all_cache()  # Hapus semua cache agar data segar
                            time.sleep(2)
                            if "hauling" in st.session_state:
                                del st.session_state["hauling"]
                            st.rerun()
                        else:
                            status.update(label="Import Gagal!", state="error", expanded=True)
                    except Exception as e:
                        status.update(label="Terjadi Kesalahan", state="error", expanded=True)
                        st.error(f"Error membaca/mengunggah Excel: {e}")

    with tab3:
        st.header("Rollback / Delete Batch")
        st.error("⚠️ Data yang dihapus tidak bisa dikembalikan. Gunakan hanya jika ada revisi salah ketik Excel.")
        
        c1, c2 = st.columns(2)
        del_date = c1.date_input("Pilih Tanggal yang Salah (Bisa Range)", value=[], key="h_date")
        del_shift = c2.selectbox("Pilih Shift", ["Semua", "DAY", "NIGHT"], key="h_shift")
        
        confirm_del = st.checkbox("Saya yakin ingin menghapus data secara permanen", key="h_confirm")
        
        if st.button(":material/delete_sweep: Hapus Batch Hauling", type="primary", disabled=not confirm_del):
            if not del_date:
                st.warning("Silakan pilih tanggal terlebih dahulu.")
            else:
                params = []
                query = "DELETE FROM coal_hauling WHERE "
                
                if len(del_date) == 2:
                    query += "date BETWEEN %s AND %s"
                    params.extend([del_date[0], del_date[1]])
                elif len(del_date) == 1:
                    query += "date = %s"
                    params.append(del_date[0])
                    
                if del_shift != "Semua":
                    query += " AND shift = %s"
                    params.append(del_shift)
                    
                if database.execute_query(query, tuple(params)):
                    st.success("Data berhasil dihapus dari server! Silakan lakukan upload ulang di tab Upload/Import.")
                    clear_all_cache()  # Hapus semua cache agar data segar
                    time.sleep(2)
                    for key in ["h_date", "h_shift", "h_confirm"]:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
                else:
                    st.error("Terjadi kegagalan saat menghapus data.")


elif menu == "Modul Overburden (OB)":
    st.title("Modul Overburden (OB)")
    st.markdown("Manajemen data pengupasan tanah (Overburden).")
    
    tab1, tab2, tab3 = st.tabs([":material/monitoring: View OB", ":material/cloud_upload: Upload OB", ":material/delete_sweep: Rollback OB"])
    
    with tab1:
        st.info("Tabel data Overburden akan tampil di sini.")
    with tab2:
        st.header("Upload Data OB")
        st.file_uploader("Upload Excel OB", type=["xlsx"], key="ob")
    with tab3:
        st.header("Rollback OB")
        st.warning("Fitur penghapusan batch OB belum aktif.")


elif menu == "Modul MS Kontrak":
    st.title("Modul MS Kontrak")
    st.markdown("Manajemen data Mine Survey dan volume kontrak.")
    
    tab1, tab2 = st.tabs([":material/monitoring: View Survey", ":material/cloud_upload: Upload Survey"])
    
    with tab1:
        st.info("Laporan hasil survey (MS) akan tampil di sini.")
    with tab2:
        st.header("Upload Laporan Survey")
        st.file_uploader("Upload Excel MS", type=["xlsx"], key="ms")


elif menu == "Modul Fuel":
    st.title("Modul Fuel")
    st.markdown("Manajemen pemakaian dan logistik bahan bakar (Fuel).")
    
    tab1, tab2, tab3 = st.tabs([":material/monitoring: View Data", ":material/cloud_upload: Upload / Import", ":material/delete_sweep: Rollback / Delete Batch"])
    
    with tab1:
        with st.expander(":material/filter_alt: Filter & Cari Data", expanded=True):
            cols = st.columns([1.5, 0.9, 1, 1, 1, 1.2, 0.7, 0.5, 0.8])
            with cols[0]:
                f_date = st.date_input("Tanggal", value=[], key="f_date_fuel")
            with cols[1]:
                f_shift = st.selectbox("Shift", ["Semua", "DAY", "NIGHT"], key="f_shift_fuel")
            with cols[2]:
                f_loc = st.selectbox("Lokasi", get_unique_locations_fuel(), key="f_loc_fuel")
            with cols[3]:
                f_vendor = st.selectbox("Vendor", get_unique_vendors_fuel(), key="f_vendor_fuel")
            with cols[4]:
                f_unit = st.selectbox("Unit", get_unique_unit_types_fuel(), key="f_unit_fuel")
            with cols[5]:
                f_search = st.text_input("Pencarian", placeholder="Voucher/ID...", key="f_search_fuel")
            with cols[6]:
                st.markdown("<div style='margin-top:26px;'></div>", unsafe_allow_html=True)
                btn_search = st.button(":material/search: Cari", type="primary", use_container_width=True, key="btn_search_fuel")
            with cols[7]:
                st.markdown("<div style='margin-top:26px;'></div>", unsafe_allow_html=True)
                if st.button(":material/refresh:", use_container_width=True, help="Tarik ulang data segar dari database", key="btn_refresh_fuel"):
                    clear_all_cache()
                    st.rerun()
            with cols[8]:
                download_placeholder = st.container()

        date_start = f_date[0] if len(f_date) >= 1 else None
        date_end = f_date[1] if len(f_date) >= 2 else None
        
        with st.spinner("Mengambil data..."):
            df = fetch_fuel_data(date_start, date_end)
        
        if not df.empty:
            if f_shift != "Semua":
                df = df[df['shift'] == f_shift]
            if f_loc != "Semua":
                df = df[df['location'] == f_loc]
            if f_vendor != "Semua":
                df = df[df['vendor'] == f_vendor]
            if f_unit != "Semua":
                df = df[df['unit_type'] == f_unit]
            if f_search:
                mask = df['unit_code'].astype(str).str.contains(f_search, case=False, na=False) | \
                       df['no_voucher'].astype(str).str.contains(f_search, case=False, na=False)
                df = df[mask]
            
        if not df.empty:
            for col in ['time']:
                if col in df.columns:
                    df[col] = df[col].astype(str).apply(lambda x: x.split()[-1] if x != 'NaT' and x != 'None' else '')
            
            for num_col in ['km', 'hm', 'refueling']:
                if num_col in df.columns:
                    df[num_col] = pd.to_numeric(df[num_col], errors='coerce')
                    
            for date_col in ['date']:
                if date_col in df.columns:
                    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                    
            df_export = df.copy()
            for col in ['km', 'hm', 'refueling']:
                if col in df_export.columns:
                    df_export[col] = df_export[col].apply(lambda x: f"{float(x):.2f}" if pd.notnull(x) else "")
            
            for d_col in ['date']:
                if d_col in df_export.columns:
                    df_export[d_col] = df_export[d_col].dt.strftime('%d/%m/%Y').fillna("")

            import io
            from openpyxl.styles import PatternFill, Font, Alignment
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_export.to_excel(writer, index=False, sheet_name='Data Fuel')
                
                workbook = writer.book
                worksheet = writer.sheets['Data Fuel']
                
                header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
                header_font = Font(color="FFFFFF", bold=True)
                
                for cell in worksheet[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    
                if len(df_export) <= 2000:
                    gray_fill = PatternFill(start_color="F4F6F9", end_color="F4F6F9", fill_type="solid")
                    for row_idx in range(2, worksheet.max_row + 1):
                        if row_idx % 2 == 0:
                            for col_idx in range(1, worksheet.max_column + 1):
                                worksheet.cell(row=row_idx, column=col_idx).fill = gray_fill
                        
                    for col in worksheet.columns:
                        max_length = 0
                        column_letter = col[0].column_letter
                        for cell in col:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        worksheet.column_dimensions[column_letter].width = min(max_length + 2, 40)

            excel_data = output.getvalue()
            
            with download_placeholder:
                st.markdown("<div style='margin-top:26px;'></div>", unsafe_allow_html=True)
                st.download_button(
                    label=":material/download: Excel",
                    data=excel_data,
                    file_name=f"Report_Fuel_{time.strftime('%Y%m%d')}.xlsx",
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    use_container_width=True,
                    key="dl_fuel"
                )
            
            col_cfg = {
                "km": st.column_config.NumberColumn("KM", format="%.2f"),
                "hm": st.column_config.NumberColumn("HM", format="%.2f"),
                "refueling": st.column_config.NumberColumn("REFUELING", format="%.2f"),
                "date": st.column_config.DateColumn("DATE", format="DD/MM/YYYY"),
                "id": None
            }
            for c in df.columns:
                if c not in col_cfg:
                    col_cfg[c] = st.column_config.Column(c.upper().replace('_', ' '))

            st.dataframe(
                df, 
                use_container_width=True, 
                hide_index=True, 
                height=700,
                column_config=col_cfg
            )
        else:
            st.info("Data fuel tidak ditemukan. Silakan ubah filter Anda.")

    with tab2:
        st.header("Update Data via Upload Excel")
        st.info("Pilih file Excel pemakaian Fuel")
        uploaded_file = st.file_uploader("Upload File Excel Fuel", type=["xlsx", "xlsb", "xls"], key="fuel_upload")
        if uploaded_file is not None:
            if st.button(":material/cloud_upload: Import ke Server", type="primary", key="btn_import_fuel"):
                with st.status("Memproses Import...", expanded=True) as status:
                    st.write("Membaca file Excel...")
                    try:
                        import numpy as np
                        df_upload = pd.read_excel(uploaded_file, sheet_name='fuel', header=0)
                        
                        st.write("Menjalankan Auto-Validator...")
                        df_upload.columns = df_upload.columns.astype(str).str.lower().str.strip().str.replace(r'\s+', '_', regex=True)
                        
                        db_cols = ['unit_fix', 'date', 'periode', 'shift', 'time', 'reg_no', 'unit_code', 'unit_model', 'unit_type', 'brand', 'vendor', 'alocation', 'km', 'hm', 'fm_awal', 'fm_akhir', 'refueling', 'source', 'location', 'operator', 'fuelman', 'no_voucher']
                        
                        available_cols = [c for c in db_cols if c in df_upload.columns]
                        df_insert = df_upload[available_cols].copy()
                        if 'no_voucher' in df_insert.columns:
                            df_insert.dropna(subset=['no_voucher'], inplace=True)
                        elif 'unit_code' in df_insert.columns:
                            df_insert.dropna(subset=['unit_code'], inplace=True)
                            
                        if 'date' in df_insert.columns:
                            df_insert['date'] = pd.to_datetime(df_insert['date'], errors='coerce').dt.strftime('%Y-%m-%d')
                            
                        if 'time' in df_insert.columns:
                            df_insert['time'] = df_insert['time'].astype(str).apply(lambda x: x.split()[-1] if x not in ['NaT', 'nan', 'None'] else None)
                        
                        df_insert = df_insert.replace({np.nan: None, pd.NaT: None, 'nan': None})
                        
                        st.write(f"Mempersiapkan {len(df_insert)} baris untuk diimport...")
                        
                        if len(df_insert) > 0:
                            placeholders = ", ".join(["%s"] * len(available_cols))
                            cols_str = ", ".join(available_cols)
                            query_insert = f"INSERT IGNORE INTO fuel ({cols_str}) VALUES ({placeholders})"
                            
                            data_to_insert = [tuple(x) for x in df_insert.to_numpy()]
                            
                            st.write("Mengimport batch data ke MySQL...")
                            success = database.execute_many_query(query_insert, data_to_insert)
                            
                            if success:
                                status.update(label="Import Selesai!", state="complete", expanded=False)
                                st.success(f"{len(df_insert)} Data Fuel berhasil diproses (duplikat diabaikan)!")
                                clear_all_cache() 
                                time.sleep(2)
                                if "fuel_upload" in st.session_state:
                                    del st.session_state["fuel_upload"]
                                st.rerun()
                            else:
                                status.update(label="Import Gagal!", state="error", expanded=True)
                        else:
                            status.update(label="Import Gagal!", state="error", expanded=True)
                            st.error("Tidak ada data valid yang ditemukan.")
                    except Exception as e:
                        status.update(label="Terjadi Kesalahan", state="error", expanded=True)
                        st.error(f"Error membaca/mengunggah Excel: {e}")

    with tab3:
        st.header("Rollback / Delete Batch")
        st.error("⚠️ Data yang dihapus tidak bisa dikembalikan. Gunakan hanya jika ada revisi salah ketik Excel.")
        
        c1, c2 = st.columns(2)
        del_date = c1.date_input("Pilih Tanggal yang Salah (Bisa Range)", value=[], key="f_del_date")
        del_shift = c2.selectbox("Pilih Shift", ["Semua", "DAY", "NIGHT"], key="f_del_shift")
        
        confirm_del = st.checkbox("Saya yakin ingin menghapus data secara permanen", key="f_confirm_del")
        
        if st.button(":material/delete_sweep: Hapus Batch Fuel", type="primary", disabled=not confirm_del, key="btn_del_fuel"):
            if not del_date:
                st.warning("Silakan pilih tanggal terlebih dahulu.")
            else:
                params = []
                query = "DELETE FROM fuel WHERE "
                
                if len(del_date) == 2:
                    query += "date BETWEEN %s AND %s"
                    params.extend([del_date[0], del_date[1]])
                elif len(del_date) == 1:
                    query += "date = %s"
                    params.append(del_date[0])
                    
                if del_shift != "Semua":
                    query += " AND shift = %s"
                    params.append(del_shift)
                    
                if database.execute_query(query, tuple(params)):
                    st.success("Data berhasil dihapus dari server! Silakan lakukan upload ulang di tab Upload/Import.")
                    clear_all_cache() 
                    time.sleep(2)
                    for key in ["f_del_date", "f_del_shift", "f_confirm_del"]:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
                else:
                    st.error("Terjadi kegagalan saat menghapus data.")
