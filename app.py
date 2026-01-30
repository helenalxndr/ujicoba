import streamlit as st
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

# =========================
# KONFIGURASI STREAMLIT
# =========================
st.set_page_config(
    page_title="Kalender Tanam Singkong",
    layout="wide"
)

st.title("🌱 Kalender Tanam Singkong Berbasis LSTM & RBS")

# =========================
# LOAD DATA & MODEL
# =========================
@st.cache_resource
def load_all():
    df = pd.read_csv("data.csv")
    df['index'] = pd.to_datetime(df['index'])

    model = load_model("model_lstm.h5")

    scaler = MinMaxScaler()
    scaler.fit(df[['curah_hujan_mm_corrected']])

    return df, model, scaler


df_all, model, scaler = load_all()

# =========================
# RBS SINGKONG
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
# SIDEBAR
# =========================
st.sidebar.header("⚙️ Pengaturan")

kecamatan_list = sorted(df_all['kecamatan'].unique())
kecamatan = st.sidebar.selectbox("Pilih Kecamatan", kecamatan_list)

tanggal_mulai = st.sidebar.date_input(
    "Tanggal Mulai Kalender",
    value=pd.to_datetime("2024-01-01")
)

# =========================
# PROSES DATA
# =========================
df_kec = df_all[df_all['kecamatan'] == kecamatan].sort_values('index')

last_30 = df_kec['curah_hujan_mm_corrected'].iloc[-30:].values
last_30_scaled = scaler.transform(last_30.reshape(-1, 1)).flatten()

pred_scaled = forecast_lstm(model, last_30_scaled, 30)
pred_mm = scaler.inverse_transform(pred_scaled.reshape(-1, 1)).flatten()

tanggal = pd.date_range(start=tanggal_mulai, periods=30, freq='D')

df_dashboard = pd.DataFrame({
    "Tanggal": tanggal,
    "Prediksi Hujan (mm)": pred_mm,
})

df_dashboard["HST"] = range(1, 31)
df_dashboard["Aktivitas"] = df_dashboard.apply(
    lambda x: rbs_singkong_final(
        x["Prediksi Hujan (mm)"],
        x["HST"]
    ),
    axis=1
)

# =========================
# RINGKASAN
# =========================
st.subheader("📊 Ringkasan Bulanan")

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
# TABEL KALENDER
# =========================
st.subheader("🗓️ Kalender Tanam (30 Hari)")

st.dataframe(
    df_dashboard,
    use_container_width=True
)

# =========================
# GRAFIK HUJAN
# =========================
st.subheader("📈 Prediksi Curah Hujan Harian")

st.line_chart(
    df_dashboard.set_index("Tanggal")["Prediksi Hujan (mm)"]
)
