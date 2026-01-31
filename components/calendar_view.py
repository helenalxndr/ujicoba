import streamlit as st
from streamlit_calendar import calendar
import pandas as pd

def render_calendar(df_dashboard, tanggal_acuan):
    # =========================
    # Build calendar events
    # =========================
    events = []
    for _, row in df_dashboard.iterrows():
        events.append({
            "title": row["Aktivitas"],
            "start": row["Tanggal"].strftime("%Y-%m-%d"),
            "allDay": True,
            "color": "#2ecc71" if row["Aktivitas"] == "Penanaman" else "#f1c40f"
        })

    # =========================
    # Render calendar
    # =========================
    state = calendar(
        events=events,
        options={
            "initialView": "dayGridMonth",
            "initialDate": tanggal_acuan.strftime("%Y-%m-%d"),
            "locale": "id",
            "height": 650,
            "headerToolbar": {
                "left": "",
                "center": "title",
                "right": ""
            },
            "fixedWeekCount": False
        },
        key="kalender"
    )

    # =========================
    # Sinkron bulan kalender
    # (PAKAI dateStr, BUKAN start UTC)
    # =========================
    if state and state.get("datesSet"):
        start_date = pd.to_datetime(
            state["datesSet"]["startStr"]
        ).date().replace(day=1)

        st.session_state["tanggal_acuan"] = start_date

    return state
