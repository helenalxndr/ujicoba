import streamlit as st
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from streamlit_calendar import calendar

# =========================
# KONFIGURASI STREAMLIT
# =========================
st.set_page_config(
    page_title="Kalender Tanam Singkong",
    layout="wide"
)

st.title("🌱 Kalender Tanam Singkong Berbasis LSTM & RBS")

# =========================
# SESSION STATE INIT
# =========================
if "tanggal_acuan" not in st.session_state:
    st.session_state["tanggal_acuan"] = pd.to_datetime("2026-01-01")

if "tanggal_dipilih" not in st.session_state:
    st.session_state["tanggal_dipilih"] = False

# =========================
# LOAD DATA & MODEL
# =========================
@st.cache_resource
def load_all():
    df = pd.read_csv("data/data.csv")
    df["index"] = pd.to_datetime(df["index"])
    model = load_model("data/model_lstm.h5", compile=False)
    scaler = MinMaxScaler()
    scaler.fit(df[["curah_hujan_mm_corrected"]])
    return df, model, scaler

df_all, model, scaler = load_all()

# =========================
# RULE BASED SYSTEM
# =========================
def rbs_singkong_final(hujan_mm, hst):
    if hst <= 14:
        return "Penanaman" if 5 <= hujan_mm <= 15 else "Pemantauan Awal"
    if 15 <= hst <= 30:
        return "Pemupukan I" if 5 <= hujan_mm <= 15 else "Tunda Pemupukan"
    if 31 <= hst <= 59:
        return "Pembersihan Hama & Gulma" if hujan_mm > 15 else "Pemantauan"
    if 60 <= hst <= 90:
        if 5 <= hujan_mm <= 15:
            return "Pemupukan II"
        elif hujan_mm > 15:
            return "Pembersihan Hama & Gulma"
        else:
            return "Tunda Pemupukan"
    if 91 <= hst <= 180:
        return "Pembersihan Hama & Gulma" if hujan_mm > 15 else "Pemantauan"
    if 181 <= hst <= 300:
        return "Panen" if hujan_mm < 10 else "Pembersihan Hama & Gulma"
    return "Tidak Disarankan"

# =========================
# FORECAST LSTM
# =========================
def forecast_lstm(model, last_window, n_days=30):
    preds = []
    window = last_window.copy()
    for _ in range(n_days):
        pred = model.predict(window.reshape(1, 30, 1), verbose=0)
        preds.append(pred[0, 0])
        window = np.append(window[1:], pred[0, 0])
    return np.array(preds)

# =========================
# PILIH KECAMATAN DAN TANGGAL
# =========================
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    kecamatan = st.selectbox(
        "Pilih Kecamatan",
        sorted(df_all["kecamatan"].unique())
    )

with col2:
    tanggal_acuan = st.date_input(
        "Tanggal Mulai Kalender",
        value=st.session_state["tanggal_acuan"]
    )
    st.session_state["tanggal_acuan"] = pd.to_datetime(tanggal_acuan)

# =========================
# PROSES DATA
# =========================
df_kec = df_all[df_all["kecamatan"] == kecamatan].sort_values("index")

last_30 = df_kec["curah_hujan_mm_corrected"].iloc[-30:].values
last_30_scaled = scaler.transform(last_30.reshape(-1, 1)).flatten()

pred_mm = scaler.inverse_transform(
    forecast_lstm(model, last_30_scaled, 30).reshape(-1, 1)
).flatten()

tanggal = pd.date_range(
    start=st.session_state["tanggal_acuan"],
    periods=30,
    freq="D"
)

df_dashboard = pd.DataFrame({
    "Tanggal": tanggal,
    "Prediksi Hujan (mm)": pred_mm
})

df_dashboard["HST"] = range(1, 31)
df_dashboard["Aktivitas"] = df_dashboard.apply(
    lambda x: rbs_singkong_final(x["Prediksi Hujan (mm)"], x["HST"]),
    axis=1
)

# =========================
# TAMPILKAN KALENDER DAN DETAIL
# =========================
col_kalender, col_detail = st.columns(2)

with col_kalender:
    events = [{
        "title": row["Aktivitas"],
        "start": row["Tanggal"].strftime("%Y-%m-%d"),
        "color": "#2ecc71" if row["Aktivitas"] == "Penanaman" else "#f1c40f"
    } for _, row in df_dashboard.iterrows()]

    state = calendar(
        events=events,
        options={
            "initialView": "dayGridMonth",
            "initialDate": st.session_state["tanggal_acuan"].strftime("%Y-%m-%d"),
            "locale": "id",
            "height": 650,
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth"
            }
        },
        key="kalender"
    )

with col_detail:
    st.header("Detail Tanggal")
    tanggal_pilih = st.selectbox(
        "Pilih Tanggal",
        df_dashboard["Tanggal"].dt.strftime("%d %B %Y")
    )
    data_tanggal = df_dashboard[df_dashboard["Tanggal"] == pd.to_datetime(tanggal_pilih)]
    
    if not data_tanggal.empty:
        st.write(f**"Prediksi Hujan: {data_tanggal['Prediksi Hujan (mm)'].values[0]} mm")
        st.write(f**"Aktivitas Rekomendasi: {data_tanggal['Aktivitas'].values[0]}")

# =========================
# RINGKASAN BULAN
# =========================
st.header("Ringkasan Bulan Ini")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Hari Tanam", 11)
with col2:
    st.metric("Hari Pupuk", 6)
with col3:
    st.metric("Hari Hama", 11)
with col4:
    st.metric("Hari Panen", 3)
