import pandas as pd
import numpy as np


def generar_datos() -> tuple[pd.DataFrame, pd.DataFrame]:
    np.random.seed(42)

    # ── pH: 48 mediciones/día (cada 30 min) ──────────────────────────────
    fechas_ph = pd.date_range("2026-05-01", "2026-06-30 23:30", freq="30min")
    n_ph = len(fechas_ph)

    ph_serpetin_daf = np.clip(np.random.normal(loc=8.5, scale=0.5, size=n_ph), 6.0, 11.0)
    ph_vertimiento  = np.clip(np.random.normal(loc=7.2, scale=0.4, size=n_ph), 5.5, 9.0)

    df_ph = pd.DataFrame({
        "fecha_hora":      fechas_ph,
        "pH_serpetin_daf": ph_serpetin_daf.round(2),
        "pH_vertimiento":  ph_vertimiento.round(2),
        "mes": np.where(fechas_ph < pd.Timestamp("2026-06-01"), "Mayo 2026", "Junio 2026"),
    })

    # ── DQO: 4 mediciones aleatorias por semana ───────────────────────────
    _todas = pd.date_range("2026-05-01", "2026-06-30", freq="D")
    _rng   = np.random.default_rng(seed=99)   # RNG independiente del pH

    _dias_sel = []
    for _, grp in pd.DataFrame({"fecha": _todas}).groupby(_todas.to_period("W")):
        idx = _rng.choice(len(grp), size=min(4, len(grp)), replace=False)
        _dias_sel.extend(grp["fecha"].iloc[sorted(idx)].tolist())

    fechas_dqo = pd.DatetimeIndex(sorted(_dias_sel))
    n_dqo      = len(fechas_dqo)

    dqo_reactor     = np.clip(np.random.normal(loc=570, scale=160, size=n_dqo), 300, 950)
    dqo_vertimiento = np.clip(np.random.normal(loc=400, scale=140, size=n_dqo), 180, 780)

    df_dqo = pd.DataFrame({
        "fecha":           fechas_dqo,
        "DQO_reactor_bio": dqo_reactor.round(1),
        "DQO_vertimiento": dqo_vertimiento.round(1),
        "mes": np.where(fechas_dqo < pd.Timestamp("2026-06-01"), "Mayo 2026", "Junio 2026"),
    })

    return df_ph, df_dqo
