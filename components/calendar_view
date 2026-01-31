from streamlit_calendar import calendar
from utils.helpers import warna_aktivitas

def render_calendar(df, tanggal_acuan):

    events = [{
        "title": row["Aktivitas"],
        "start": row["Tanggal"].strftime("%Y-%m-%d"),
        "color": warna_aktivitas(row["Aktivitas"])
    } for _, row in df.iterrows()]

    state = calendar(
        events=events,
        options={
            "initialView": "dayGridMonth",
            "initialDate": tanggal_acuan.strftime("%Y-%m-%d"),
            "locale": "id",
            "height": 650
        },
        key="kalender"
    )

    return state
