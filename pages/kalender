import streamlit as st
from components.header import render_header
from components.calendar_view import render_calendar
from components.detail_panel import render_detail_panel
from components.summary_cards import render_summary
from utils.data_loader import load_all
from utils.forecast import build_dashboard_df

df_all, model, scaler = load_all()

kecamatan, tanggal_acuan = render_header(df_all)

df_dashboard = build_dashboard_df(
    df_all, model, scaler, kecamatan, tanggal_acuan
)

col_kal, col_detail = st.columns([3, 2])

with col_kal:
    calendar_state = render_calendar(df_dashboard, tanggal_acuan)

with col_detail:
    render_detail_panel(df_dashboard, calendar_state)

render_summary(df_dashboard)
