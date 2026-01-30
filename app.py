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
st.caption("Prediksi curah hujan harian menggunakan LSTM dan rekomendasi aktivitas berbasis Rule-Based System")

# =========================
# LOAD DATA & MODEL
# =========================
@st.cache_resource
def load_all():
    df = pd.read_csv("data.csv")
    df["index"] = pd.to_datetime(df["index"])

    model = load_model("model_lstm.h5", compile=False)

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
# SESSION STATE (TANGGAL)
# =========================
if "tanggal_mulai" not in st.session_state:
    st.session_state["tanggal_mulai"] = pd.to_datetime("2024-01-01")

# =========================
# SIDEBAR
# =========================
st.sidebar.header("⚙️ Pengaturan")

kecamatan_list = sorted(df_all["kecamatan"].unique())
kecamatan = st.sidebar.selectbox("Pilih Kecamatan", kecamatan_list)

tanggal_mulai = st.sidebar.date_input(
    "Tanggal Mulai Kalender",
    value=st.session_state["tanggal_mulai"],
    key="tanggal_mulai"
)

# =========================
# PROSES DATA
# =========================
df_kec = df_all[df_all["kecamatan"] == kecamatan].sort_values("index")

if len(df_kec) < 30:
    st.warning("⚠️ Data historis kurang dari 30 hari.")
    st.stop()

last_30 = df_kec["curah_hujan_mm_corrected"].iloc[-30:].values
last_30_scaled = scaler.transform(last_30.reshape(-1, 1)).flatten()

pred_scaled = forecast_lstm(model, last_30_scaled, 30)
pred_mm = scaler.inverse_transform(pred_scaled.reshape(-1, 1)).flatten()

tanggal = pd.date_range(
    start=st.session_state["tanggal_mulai"],
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
# WARNA AKTIVITAS
# =========================
def aktivitas_color(aktivitas):
    if aktivitas == "Penanaman":
        return "#2ecc71"
    if "Pemupukan" in aktivitas:
        return "#f1c40f"
    if "Hama" in aktivitas:
        return "#e74c3c"
    if aktivitas == "Panen":
        return "#8e44ad"
    return "#3498db"


# =========================
# RINGKASAN
# =========================
st.subheader("📊 Ringkasan Kalender Tanam")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Rata-rata Curah Hujan",
    f"{df_dashboard['Prediksi Hujan (mm)'].mean():.2f} mm/hari"
)

col2.metric(
    "Aktivitas Dominan",
    df_dashboard["Aktivitas"].value_counts().idxmax()
)

col3.metric(
    "Hari Penanaman",
    (df_dashboard["Aktivitas"] == "Penanaman").sum()
)

# =========================
# KALENDER INTERAKTIF
# =========================
st.subheader("🗓️ Kalender Tanam Singkong (Interaktif)")

events = []
for _, row in df_dashboard.iterrows():
    events.append({
        "title": row["Aktivitas"],
        "start": row["Tanggal"].strftime("%Y-%m-%d"),
        "end": row["Tanggal"].strftime("%Y-%m-%d"),
        "color": aktivitas_color(row["Aktivitas"]),
        "extendedProps": {
            "HST": row["HST"],
            "Hujan": f"{row['Prediksi Hujan (mm)']:.2f} mm"
        }
    })

calendar_options = {
    "initialView": "dayGridMonth",
    "initialDate": st.session_state["tanggal_mulai"].strftime("%Y-%m-%d"),
    "locale": "id",
    "height": 650,
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek"
    }
}

state = calendar(
    events=events,
    options=calendar_options,
    key="kalender_singkong"
)

# =========================
# SINKRON ARROW ↔ SIDEBAR
# =========================
if state.get("datesSet"):
    start_date = pd.to_datetime(state["datesSet"]["start"]).date()
    st.session_state["tanggal_mulai"] = start_date.replace(day=1)

# =========================
# DETAIL EVENT
# =========================
if state.get("eventClick"):
    e = state["eventClick"]["event"]
    st.info(
        f"""
        📅 **Tanggal**: {e['start']}
        🌱 **Aktivitas**: {e['title']}
        📊 **Curah Hujan**: {e['extendedProps']['Hujan']}
        ⏳ **HST**: {e['extendedProps']['HST']}
        """
    )

# =========================
# GRAFIK HUJAN
# =========================
st.subheader("📈 Prediksi Curah Hujan Harian")

st.line_chart(
    df_dashboard.set_index("Tanggal")["Prediksi Hujan (mm)"]
)
