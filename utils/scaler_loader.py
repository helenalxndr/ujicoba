import joblib
from pathlib import Path

SCALER_DIR = Path("data/scaler")

def load_scaler(kecamatan: str):
    scaler_path = SCALER_DIR / f"scaler_{kecamatan}.pkl"

    if not scaler_path.exists():
        raise FileNotFoundError(
            f"Scaler untuk kecamatan {kecamatan} tidak ditemukan"
        )

    return joblib.load(scaler_path)
