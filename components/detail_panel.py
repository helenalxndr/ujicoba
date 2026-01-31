import streamlit as st
import pandas as pd

def render_detail_panel(df_dashboard, calendar_state):
    st.subheader("📌 Detail Aktivitas")

    if not calendar_state:
        st.info("Klik tanggal atau aktivitas di kalender.")
        return

    selected_date = None

    # ✅ 1. PRIORITAS: EVENT CLICK (klik bar aktivitas)
    if "eventClick" in calendar_state:
        selected_date = pd.to_datetime(
            calendar_state["eventClick"]["event"]["start"]
        ).date()

    # ✅ 2. DATE CLICK (jika aktif)
    elif "dateClick" in calendar_state:
        selected_date = pd.to_datetime(
            calendar_state["dateClick"]["date"]
        ).date()

    # ✅ 3. SELECT (klik sel kalender)
    elif "select" in calendar_state:
        # 🔥 start UTC → convert ke tanggal lokal
        selected_date = (
            pd.to_datetime(calendar_state["select"]["start"], utc=True)
            .tz_convert("Asia/Jakarta")
            .date()
        )

    if not selected_date:
        st.info("Klik tanggal atau aktivitas di kalender.")
        return

    # 🔍 Cari data
    data_hari = df_dashboard[
        df_dashboard["Tanggal"].dt.date == selected_date
    ]

    if data_hari.empty:
        st.warning(f"Tidak ada data aktivitas untuk {selected_date}")
        return

    row = data_hari.iloc[0]

    st.markdown(f"""
    **🗓️ Tanggal:** {row['Tanggal'].strftime('%d %B %Y')}  
    **🌧️ Prediksi Hujan:** {row['Prediksi_Hujan']:.2f} mm  
    **🌱 HST:** {row['HST']}  
    **📋 Aktivitas:** **{row['Aktivitas']}**
    """)
