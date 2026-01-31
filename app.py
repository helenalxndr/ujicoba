import streamlit as st

st.set_page_config(
    page_title="Kalender Tanam Singkong",
    layout="wide"
)

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("🌱 Kalender Tanam Singkong")
st.caption("Silakan buka halaman **Kalender** melalui menu Pages.")
