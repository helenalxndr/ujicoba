import pandas as pd
import streamlit as st
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler


@st.cache_resource
def load_all():
    """
    Load dataset, model LSTM, dan scaler.
    Scaler di-fit satu kali menggunakan seluruh data historis.
    """

    # Load data
    df = pd.read_csv("data/data.csv")
    df["index"] = pd.to_datetime(df["index"])

    # Load model
    model = load_model(
        "data/model_lstm.h5",
        compile=False
    )

    # Inisialisasi & fit scaler
    scaler = MinMaxScaler()
    scaler.fit(df[["curah_hujan_mm_corrected"]])

    return df, model, scaler
