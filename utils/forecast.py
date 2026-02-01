import numpy as np
import pandas as pd
from utils.rbs import rbs_singkong_final
from utils.scaler_loader import load_scaler

WINDOW_SIZE = 30


def forecast_lstm(model, last_window, n_days=30):
    """
    Recursive forecasting menggunakan model LSTM.
    Input harus dalam kondisi sudah di-scale.
    """

    preds = []
    window = last_window.copy()

    for _ in range(n_days):
        pred = model.predict(
            window.reshape(1, WINDOW_SIZE, 1),
            verbose=0
        )
        preds.append(pred[0, 0])
        window = np.append(window[1:], pred[0, 0])

    return np.array(preds)


def build_dashboard_df(
    df_all,
    model,
    kecamatan,
    tanggal_acuan,
    n_days=30
):
    """
    Menyusun dataframe final untuk dashboard kalender tanam.
    Seluruh proses scaling dilakukan di sini.
    """

    # ===============================
    # LOAD SCALER PER KECAMATAN
    # ===============================
    scaler = load_scaler(kecamatan)

    # ===============================
    # FILTER DATA
    # ===============================
    df_kec = (
        df_all[df_all["kecamatan"] == kecamatan]
        .sort_values("index")
    )

    if len(df_kec) < WINDOW_SIZE:
        return pd.DataFrame()

    # ===============================
    # AMBIL WINDOW TERAKHIR
    # ===============================
    last_window = (
        df_kec["curah_hujan_mm_corrected"]
        .iloc[-WINDOW_SIZE:]
        .values
    )

    # ===============================
    # SCALING
    # ===============================
    last_scaled = scaler.transform(
        last_window.reshape(-1, 1)
    ).flatten()

    # ===============================
    # FORECAST
    # ===============================
    pred_scaled = forecast_lstm(
        model,
        last_scaled,
        n_days
    )

    # ===============================
    # INVERSE SCALING
    # ===============================
    pred_mm = scaler.inverse_transform(
        pred_scaled.reshape(-1, 1)
    ).flatten()

    # ===============================
    # BUILD DATAFRAME
    # ===============================
    tanggal = pd.date_range(
        start=tanggal_acuan,
        periods=n_days,
        freq="D"
    )

    df_dashboard = pd.DataFrame({
        "Tanggal": tanggal,
        "Prediksi Hujan (mm)": pred_mm,
        "HST": range(1, n_days + 1)
    })

    df_dashboard["Aktivitas"] = df_dashboard.apply(
        lambda x: rbs_singkong_final(
            x["Prediksi Hujan (mm)"],
            x["HST"]
        ),
        axis=1
    )

    return df_dashboard
