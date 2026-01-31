import numpy as np
import pandas as pd
from utils.rbs import rbs_singkong_final


def forecast_lstm(model, last_window, n_days=30):
    """
    Forecast curah hujan menggunakan model LSTM
    dengan pendekatan recursive forecasting.
    """

    preds = []
    window = last_window.copy()

    for _ in range(n_days):
        pred = model.predict(
            window.reshape(1, 30, 1),
            verbose=0
        )
        preds.append(pred[0, 0])
        window = np.append(window[1:], pred[0, 0])

    return np.array(preds)


def build_dashboard_df(
    df_all,
    model,
    scaler,
    kecamatan,
    tanggal_acuan,
    n_days=30
):
    """
    Menyusun dataframe final untuk dashboard kalender.
    """

    # Filter kecamatan
    df_kec = (
        df_all[df_all["kecamatan"] == kecamatan]
        .sort_values("index")
    )

    # Ambil 30 hari terakhir
    last_30 = (
        df_kec["curah_hujan_mm_corrected"]
        .iloc[-30:]
        .values
    )

    # Scaling
    last_30_scaled = scaler.transform(
        last_30.reshape(-1, 1)
    ).flatten()

    # Forecast
    pred_scaled = forecast_lstm(
        model,
        last_30_scaled,
        n_days
    )

    # Inverse scaling
    pred_mm = scaler.inverse_transform(
        pred_scaled.reshape(-1, 1)
    ).flatten()

    # Buat tanggal
    tanggal = pd.date_range(
        start=tanggal_acuan,
        periods=n_days,
        freq="D"
    )

    # Dataframe dashboard
    df_dashboard = pd.DataFrame({
        "Tanggal": tanggal,
        "Prediksi Hujan (mm)": pred_mm
    })

    df_dashboard["HST"] = range(1, n_days + 1)

    df_dashboard["Aktivitas"] = df_dashboard.apply(
        lambda x: rbs_singkong_final(
            x["Prediksi Hujan (mm)"],
            x["HST"]
        ),
        axis=1
    )

    return df_dashboard
