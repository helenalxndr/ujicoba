import streamlit as st
import pandas as pd

def render_detail_panel(df, calendar_state):
    st.subheader("Detail Tanggal")

    if calendar_state.get("eventClick"):
        tanggal = pd.to_datetime(
            calendar_state["eventClick"]["event"]["start"]
        )

        row = df[df["Tanggal"] == tanggal].iloc[0]

        st.markdown(f"**{tanggal.strftime('%A, %d %B %Y')}**")
        st.metric(
            "🌧️ Prediksi Hujan",
            f"{row['Prediksi Hujan (mm)']:.1f} mm"
        )
        st.info(f"**Rekomendasi:** {row['Aktivitas']}")

    else:
        st.caption("Klik tanggal pada kalender untuk melihat detail.")
