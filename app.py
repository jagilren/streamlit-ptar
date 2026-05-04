import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

from data import generar_datos

st.set_page_config(
    page_title="Dashboard PTAR D'Vida — pH y DQO",
    page_icon="💧",
    layout="wide",
)

PH_MIN = 6.0
PH_MAX = 9.0

COLOR_REACTOR = "#7C4DFF"
COLOR_VERT    = "#FF5722"
COLOR_PH_DAF  = "#00ACC1"
COLOR_PH_VERT = "#43A047"

SERIES_DQO = {
    "DQO_reactor_bio": {
        "label":  "Reactor Biológico",
        "color":  COLOR_REACTOR,
        "limite": None,
        "norma":  None,
        "bg_exc": "#EDE7F6",
    },
    "DQO_vertimiento": {
        "label":  "Vertimiento",
        "color":  COLOR_VERT,
        "limite": 700.0,
        "norma":  "Res. 0631/2015",
        "bg_exc": "#FFCDD2",
    },
}

st.title("💧 Dashboard PTAR")
st.markdown("Monitoreo de parámetros de calidad de agua · 2026")
st.divider()

df_ph, df_dqo = generar_datos()

_MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}
_OPCIONES_MES = ["Todos", "Mayo 2026", "Junio 2026"]
_ahora = datetime.now()
_mes_actual = f"{_MESES_ES[_ahora.month]} {_ahora.year}"
_idx_default = _OPCIONES_MES.index(_mes_actual) if _mes_actual in _OPCIONES_MES else 0

with st.sidebar:
    st.header("Filtros")
    mes_sel = st.selectbox("Mes", _OPCIONES_MES, index=_idx_default)

    if mes_sel != "Todos":
        _dias = df_ph[df_ph["mes"] == mes_sel]["fecha_hora"].dt.day
        _semanas_disp = sorted((((_dias - 1) // 7) + 1).unique())
        _opciones_sem = ["Todas"] + [f"Semana {s}" for s in _semanas_disp]
        sem_sel = st.selectbox("Semana", _opciones_sem)
    else:
        sem_sel = "Todas"

df_ph_f  = df_ph[df_ph["mes"] == mes_sel].reset_index(drop=True)   if mes_sel != "Todos" else df_ph.copy()
df_dqo_f = df_dqo[df_dqo["mes"] == mes_sel].reset_index(drop=True) if mes_sel != "Todos" else df_dqo.copy()

if sem_sel != "Todas":
    _n = int(sem_sel.split()[-1])
    df_ph_f  = df_ph_f[((df_ph_f["fecha_hora"].dt.day  - 1) // 7 + 1) == _n].reset_index(drop=True)
    df_dqo_f = df_dqo_f[((df_dqo_f["fecha"].dt.day - 1) // 7 + 1) == _n].reset_index(drop=True)

# ============================================================
# TABS PRINCIPALES
# ============================================================
tab_ph, tab_dqo, tab_datos = st.tabs(["🟠 DQO (mg/L)","🔵 pH", "📋 Datos"])

# ============================================================
# TAB pH
# ============================================================
with tab_ph:
    n_med = len(df_ph_f)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Serpentín DAF — Máx.", f"{df_ph_f['pH_serpetin_daf'].max():.2f}")
    col2.metric("Serpentín DAF — Mín.", f"{df_ph_f['pH_serpetin_daf'].min():.2f}")
    col3.metric("Vertimiento — Máx.", f"{df_ph_f['pH_vertimiento'].max():.2f}")
    col4.metric("Vertimiento — Mín.", f"{df_ph_f['pH_vertimiento'].min():.2f}")

    exc_daf = int(
        ((df_ph_f["pH_serpetin_daf"] < PH_MIN) | (df_ph_f["pH_serpetin_daf"] > PH_MAX)).sum()
    )
    exc_vert_ph = int(
        ((df_ph_f["pH_vertimiento"] < PH_MIN) | (df_ph_f["pH_vertimiento"] > PH_MAX)).sum()
    )
    col5, col6 = st.columns(2)
    col5.metric("Mediciones fuera de rango — DAF", f"{exc_daf} / {n_med} ({exc_daf / n_med * 100:.1f}%)")
    col6.metric("Mediciones fuera de rango — Vert.", f"{exc_vert_ph} / {n_med} ({exc_vert_ph / n_med * 100:.1f}%)")

    st.divider()

    # Gráfica de línea — ambas series en el mismo canvas
    fig_ph = go.Figure()
    fig_ph.add_trace(go.Scatter(
        x=df_ph_f["fecha_hora"],
        y=df_ph_f["pH_serpetin_daf"],
        mode="lines",
        line=dict(color=COLOR_PH_DAF, width=1),
        name="Serpentín DAF",
    ))
    fig_ph.add_trace(go.Scatter(
        x=df_ph_f["fecha_hora"],
        y=df_ph_f["pH_vertimiento"],
        mode="lines",
        line=dict(color=COLOR_PH_VERT, width=1),
        name="Vertimiento",
    ))
    fig_ph.add_hline(
        y=PH_MIN, line_dash="dash", line_color="orange",
        annotation_text="Mínimo (6.0)", annotation_position="bottom right",
    )
    fig_ph.add_hline(
        y=PH_MAX, line_dash="dash", line_color="red",
        annotation_text="Máximo (9.0)", annotation_position="top right",
    )
    fig_ph.update_layout(
        xaxis=dict(title="Fecha / Hora", tickformat="%d %b"),
        yaxis=dict(title="pH", range=[4.5, 11.5]),
        hovermode="x unified",
        height=420,
        margin=dict(l=40, r=40, t=20, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    st.plotly_chart(fig_ph, use_container_width=True)

    st.divider()

    # Tablas de excedencias por punto
    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.markdown("**🔵 Serpentín DAF — Mediciones fuera de rango [6.0 – 9.0]**")
        df_exc_daf = df_ph_f[
            (df_ph_f["pH_serpetin_daf"] < PH_MIN) | (df_ph_f["pH_serpetin_daf"] > PH_MAX)
        ].copy()
        if df_exc_daf.empty:
            st.success("Sin excedencias en Serpentín DAF.")
        else:
            df_show = df_exc_daf[["fecha_hora", "pH_serpetin_daf", "mes"]].copy()
            df_show["fecha_hora"] = df_show["fecha_hora"].dt.strftime("%d/%m/%Y %H:%M")
            df_show.columns = ["Fecha / Hora", "pH Serpentín DAF", "Mes"]
            st.dataframe(
                df_show.style.format({"pH Serpentín DAF": "{:.2f}"}).set_properties(
                    **{"background-color": "#E0F7FA", "color": "#000000"}
                ),
                use_container_width=True, hide_index=True,
            )

    with col_t2:
        st.markdown("**🟢 Vertimiento — Mediciones fuera de rango [6.0 – 9.0]**")
        df_exc_vert_ph = df_ph_f[
            (df_ph_f["pH_vertimiento"] < PH_MIN) | (df_ph_f["pH_vertimiento"] > PH_MAX)
        ].copy()
        if df_exc_vert_ph.empty:
            st.success("Sin excedencias en Vertimiento.")
        else:
            df_show = df_exc_vert_ph[["fecha_hora", "pH_vertimiento", "mes"]].copy()
            df_show["fecha_hora"] = df_show["fecha_hora"].dt.strftime("%d/%m/%Y %H:%M")
            df_show.columns = ["Fecha / Hora", "pH Vertimiento", "Mes"]
            st.dataframe(
                df_show.style.format({"pH Vertimiento": "{:.2f}"}).set_properties(
                    **{"background-color": "#E8F5E9", "color": "#000000"}
                ),
                use_container_width=True, hide_index=True,
            )

    st.divider()

    st.subheader("Tabla de mediciones — pH (cada 30 min)")
    df_ph_tabla = df_ph_f[["fecha_hora", "pH_serpetin_daf", "pH_vertimiento", "mes"]].copy()
    df_ph_tabla["fecha_hora"] = df_ph_tabla["fecha_hora"].dt.strftime("%d/%m/%Y %H:%M")
    df_ph_tabla.columns = ["Fecha / Hora", "pH Serpentín DAF", "pH Vertimiento", "Mes"]
    st.dataframe(
        df_ph_tabla.style.format({"pH Serpentín DAF": "{:.2f}", "pH Vertimiento": "{:.2f}"}),
        use_container_width=True, hide_index=True,
    )

# ============================================================
# TAB DQO
# ============================================================
with tab_dqo:
    n_dias = len(df_dqo_f)

    # Fichas Máx / Mín — todas las series
    _cols_mm = st.columns(len(SERIES_DQO) * 2)
    for i, (col_key, cfg) in enumerate(SERIES_DQO.items()):
        _cols_mm[i * 2].metric(f"{cfg['label']} — Máx. (mg/L)", f"{df_dqo_f[col_key].max():.1f}")
        _cols_mm[i * 2 + 1].metric(f"{cfg['label']} — Mín. (mg/L)", f"{df_dqo_f[col_key].min():.1f}")

    # Fichas Días sobre límite — solo series con restricción normativa
    _reg = {k: v for k, v in SERIES_DQO.items() if v["limite"] is not None}
    if _reg:
        _cols_reg = st.columns(len(_reg))
        for i, (col_key, cfg) in enumerate(_reg.items()):
            _exc = int((df_dqo_f[col_key] >= cfg["limite"]).sum())
            _cols_reg[i].metric(
                f"Días sobre límite — {cfg['label']} ({cfg['norma']})",
                f"{_exc} / {n_dias} ({_exc / n_dias * 100:.1f}%)",
            )

    st.divider()

    # Gráfica de barras agrupadas — todas las series
    fig_dqo_bar = go.Figure()
    for col_key, cfg in SERIES_DQO.items():
        fig_dqo_bar.add_trace(go.Bar(
            x=df_dqo_f["fecha"], y=df_dqo_f[col_key],
            name=cfg["label"], marker_color=cfg["color"],
        ))
    for col_key, cfg in SERIES_DQO.items():
        if cfg["limite"] is not None:
            fig_dqo_bar.add_hline(
                y=cfg["limite"], line_dash="dash", line_color="red",
                annotation_text=cfg["norma"], annotation_position="top left",
            )
    fig_dqo_bar.update_layout(
        barmode="group", height=280,
        margin=dict(l=20, r=20, t=10, b=40),
        xaxis=dict(tickformat="%d %b"),
        yaxis=dict(title="DQO (mg/L)", range=[100, 1100]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    st.plotly_chart(fig_dqo_bar, use_container_width=True)

    # Gráfica de línea — todas las series
    fig_dqo_line = go.Figure()
    for col_key, cfg in SERIES_DQO.items():
        fig_dqo_line.add_trace(go.Scatter(
            x=df_dqo_f["fecha"], y=df_dqo_f[col_key],
            mode="lines+markers",
            line=dict(color=cfg["color"], width=2), marker=dict(size=6),
            name=cfg["label"],
        ))
    for col_key, cfg in SERIES_DQO.items():
        if cfg["limite"] is not None:
            fig_dqo_line.add_hline(
                y=cfg["limite"], line_dash="dash", line_color="red",
                annotation_text=f"Límite máx. {cfg['norma']} ({cfg['limite']:.0f} mg/L)",
                annotation_position="top right",
            )
    fig_dqo_line.update_layout(
        xaxis=dict(title="Fecha", tickformat="%d %b"),
        yaxis=dict(title="DQO (mg/L)", range=[100, 1100]),
        hovermode="x unified", height=380,
        margin=dict(l=40, r=40, t=20, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    st.plotly_chart(fig_dqo_line, use_container_width=True)

    st.divider()

    # Tablas de excedencias — solo series con restricción normativa
    if _reg:
        _cols_exc = st.columns(len(_reg))
        for i, (col_key, cfg) in enumerate(_reg.items()):
            with _cols_exc[i]:
                st.markdown(f"**Días ≥ {cfg['limite']:.0f} mg/L — {cfg['label']} ({cfg['norma']})**")
                df_exc = df_dqo_f[df_dqo_f[col_key] >= cfg["limite"]].copy()
                if df_exc.empty:
                    st.success(f"Ningún día superó el límite en {cfg['label']}.")
                else:
                    df_show = df_exc[["fecha", col_key, "mes"]].copy()
                    df_show["fecha"] = df_show["fecha"].dt.strftime("%d/%m/%Y")
                    df_show.columns = ["Fecha", "DQO (mg/L)", "Mes"]
                    st.dataframe(
                        df_show.style.format({"DQO (mg/L)": "{:.1f}"}).set_properties(
                            **{"background-color": cfg["bg_exc"], "color": "#000000"}
                        ),
                        use_container_width=True, hide_index=True,
                    )

    st.divider()

    # Tabla completa de valores
    st.subheader("Tabla de valores — DQO")
    _cols_t = ["fecha"] + list(SERIES_DQO.keys()) + ["mes"]
    df_dqo_tabla = df_dqo_f[_cols_t].copy()
    df_dqo_tabla["fecha"] = df_dqo_tabla["fecha"].dt.strftime("%d/%m/%Y")
    df_dqo_tabla.columns = (
        ["Fecha"] + [f"{cfg['label']} (mg/L)" for cfg in SERIES_DQO.values()] + ["Mes"]
    )
    st.dataframe(
        df_dqo_tabla.style.format(
            {f"{cfg['label']} (mg/L)": "{:.1f}" for cfg in SERIES_DQO.values()}
        ),
        use_container_width=True, hide_index=True,
    )

# ============================================================
# TAB DATOS
# ============================================================
with tab_datos:
    st.subheader("Mediciones de pH — cada 30 min")
    df_ph_tabla = df_ph_f[["fecha_hora", "pH_serpetin_daf", "pH_vertimiento", "mes"]].copy()
    df_ph_tabla["fecha_hora"] = df_ph_tabla["fecha_hora"].dt.strftime("%d/%m/%Y %H:%M")
    df_ph_tabla.columns = ["Fecha / Hora", "pH Serpentín DAF", "pH Vertimiento", "Mes"]
    st.dataframe(
        df_ph_tabla.style.format({"pH Serpentín DAF": "{:.2f}", "pH Vertimiento": "{:.2f}"}),
        use_container_width=True, hide_index=True,
    )

    st.divider()

    st.subheader("Mediciones de DQO — 4 días/semana")
    _cols_t2 = ["fecha"] + list(SERIES_DQO.keys()) + ["mes"]
    df_dqo_tabla2 = df_dqo_f[_cols_t2].copy()
    df_dqo_tabla2["fecha"] = df_dqo_tabla2["fecha"].dt.strftime("%d/%m/%Y")
    df_dqo_tabla2.columns = (
        ["Fecha"] + [f"{cfg['label']} (mg/L)" for cfg in SERIES_DQO.values()] + ["Mes"]
    )
    st.dataframe(
        df_dqo_tabla2.style.format(
            {f"{cfg['label']} (mg/L)": "{:.1f}" for cfg in SERIES_DQO.values()}
        ),
        use_container_width=True, hide_index=True,
    )
