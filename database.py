import mysql.connector
import pandas as pd
import streamlit as st

# =========================================================================
# PERBAIKAN 1: Kredensial dibaca dari st.secrets (bukan hardcode)
# PERBAIKAN 2: Setiap fungsi membuka & menutup koneksi sendiri (try/finally)
#              → Menghilangkan connection leak
# =========================================================================

def _get_db_config():
    """Membaca konfigurasi DB dari st.secrets (secrets.toml atau Streamlit Cloud)."""
    return {
        "host":     st.secrets["database"]["host"],
        "port":     int(st.secrets["database"]["port"]),
        "user":     st.secrets["database"]["user"],
        "password": st.secrets["database"]["password"],
        "database": st.secrets["database"]["database"],
        "connection_timeout": 30,
    }

def _new_connection():
    """Membuka koneksi MySQL baru. Mengembalikan None jika gagal."""
    try:
        return mysql.connector.connect(**_get_db_config())
    except Exception as e:
        st.error(f"❌ Gagal terhubung ke database: {e}")
        return None

# -------------------------------------------------------------------------
# fetch_data — SELECT query, kembalikan DataFrame
# -------------------------------------------------------------------------
def fetch_data(query, params=None):
    conn = _new_connection()
    if conn is None:
        return pd.DataFrame()
    try:
        df = pd.read_sql(query, conn, params=params)
        return df
    except Exception as e:
        st.error(f"❌ Error membaca data: {e}")
        return pd.DataFrame()
    finally:
        conn.close()  # Selalu ditutup, bahkan jika terjadi error

# -------------------------------------------------------------------------
# execute_query — INSERT / UPDATE / DELETE satu query
# -------------------------------------------------------------------------
def execute_query(query, params=None):
    conn = _new_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(query, params) if params else cursor.execute(query)
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        st.error(f"❌ Error eksekusi query: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()  # Selalu ditutup, bahkan jika terjadi error

# -------------------------------------------------------------------------
# execute_many_query — Batch INSERT (upload massal dari Excel)
# -------------------------------------------------------------------------
def execute_many_query(query, params_list):
    conn = _new_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        st.error(f"❌ Error batch insert: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()  # Selalu ditutup, bahkan jika terjadi error
