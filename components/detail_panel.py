def render_detail_panel(df_dashboard, calendar_state):

    if not calendar_state:
        return

    #SATU-SATUNYA YANG BENAR
    if "event" not in calendar_state:
        return

    selected_date = pd.to_datetime(
        calendar_state["event"]["dateStr"]
    ).date()

    data_hari = df_dashboard[
        df_dashboard["Tanggal"].dt.date == selected_date
    ]

    if data_hari.empty:
        st.info("Tidak ada aktivitas pada tanggal ini")
        return

    row = data_hari.iloc[0]

    st.markdown("### 📌 Detail Aktivitas")
    st.write(f"📅 Tanggal: {row['Tanggal'].strftime('%d %B %Y')}")
    st.write(f"🌧️ Prediksi Hujan: {row['Prediksi_Hujan']:.2f} mm")
    st.write(f"🌱 HST: {row['HST']}")
    st.write(f"📋 Aktivitas: {row['Aktivitas']}")
