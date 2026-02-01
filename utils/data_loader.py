import pandas as pd
import streamlit as st
import joblib
from tensorflow.keras.models import load_model

@st.cache_resource
def load_all():
    df = pd.read_csv("data/data.csv")
    df["index"] = pd.to_datetime(df["index"])

    model = load_model("data/model_lstm.h5", compile=False)
    scaler = joblib.load("data/scaler_rainfall.pkl")

    return df, model, scaler
