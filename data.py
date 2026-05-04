import pandas as pd
import numpy as np


def generar_datos() -> pd.DataFrame:
    np.random.seed(42)

    fechas_mayo = pd.date_range("2026-05-01", "2026-05-31", freq="D")
    fechas_junio = pd.date_range("2026-06-01", "2026-06-30", freq="D")
    fechas = pd.DatetimeIndex(list(fechas_mayo) + list(fechas_junio))

    n = len(fechas)

    ph = np.clip(np.random.normal(loc=7.2, scale=0.6, size=n), 9.0, 9.5)
    dqo = np.clip(np.random.normal(loc=550, scale=180, size=n), 300, 1000)

    meses = (
        ["Mayo 2026"] * len(fechas_mayo) + ["Junio 2026"] * len(fechas_junio)
    )

    return pd.DataFrame(
        {
            "fecha": fechas,
            "pH": ph.round(2),
            "DQO_mg_L": dqo.round(1),
            "mes": meses,
        }
    )
