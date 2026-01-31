import streamlit as st
import pandas as pd

def render_detail_panel(df_dashboard, calendar_state):
    st.subheader("📌 Detail Aktivitas")

    if not calendar_state:
        st.info("Klik salah satu tanggal di kalender untuk melihat detail.")
        return

    # 🔥 SATU-SATUNYA YANG BENAR
    if "event" not in calendar_state:
        st.info("Klik salah satu tanggal di kalender untuk melihat detail.")
        return

    selected_date = pd.to_datetime(
        calendar_state["event"]["dateStr"]
    ).date()

    data_hari = df_dashboard[
        df_dashboard["Tanggal"].dt.date == selected_date
    ]

    if data_hari.empty:
        st.warning("Tidak ada data untuk tanggal ini.")
        return

    row = data_hari.iloc[0]

    st.markdown(f"""
    **🗓️ Tanggal:** {row['Tanggal'].strftime('%d %B %Y')}  
    **🌧️ Prediksi Hujan:** {row['Prediksi_Hujan']:.2f} mm  
    **🌱 HST:** {row['HST']}  
    **📋 Aktivitas:** **{row['Aktivitas']}**
    """)
