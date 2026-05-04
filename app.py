import streamlit as st
import plotly.graph_objects as go

from data import generar_datos

st.set_page_config(
    page_title="Dashboard PTAR D'Vida — pH y DQO",
    page_icon="💧",
    layout="wide",
)

PH_MIN     = 6.0
PH_MAX     = 9.0
DQO_LIMITE = 700.0  # Resolución 0631/2015

COLOR_REACTOR = "#7C4DFF"  # violeta — Reactor biológico
COLOR_VERT    = "#FF5722"  # naranja-rojo — DQO Vertimiento
COLOR_PH_DAF  = "#00ACC1"  # cian — pH Serpentín DAF
COLOR_PH_VERT = "#43A047"  # verde — pH Vertimiento

st.title("💧 Dashboard PTAR — pH y DQO")
st.markdown("Monitoreo de parámetros de calidad de agua · 2026")
st.divider()

df_ph, df_dqo = generar_datos()

with st.sidebar:
    st.header("Filtros")
    mes_sel = st.selectbox("Mes", ["Todos", "Mayo 2026", "Junio 2026"])

df_ph_f  = df_ph[df_ph["mes"] == mes_sel].reset_index(drop=True)   if mes_sel != "Todos" else df_ph.copy()
df_dqo_f = df_dqo[df_dqo["mes"] == mes_sel].reset_index(drop=True) if mes_sel != "Todos" else df_dqo.copy()

# ============================================================
# TABS PRINCIPALES
# ============================================================
tab_ph, tab_dqo, tab_datos = st.tabs(["🔵 pH", "🟠 DQO (mg/L)", "📋 Datos"])

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
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Reactor Bio — Máx. (mg/L)", f"{df_dqo_f['DQO_reactor_bio'].max():.1f}")
    col2.metric("Reactor Bio — Mín. (mg/L)", f"{df_dqo_f['DQO_reactor_bio'].min():.1f}")
    col3.metric("Vertimiento — Máx. (mg/L)", f"{df_dqo_f['DQO_vertimiento'].max():.1f}")
    col4.metric("Vertimiento — Mín. (mg/L)", f"{df_dqo_f['DQO_vertimiento'].min():.1f}")

    exc_reactor = int((df_dqo_f["DQO_reactor_bio"] >= DQO_LIMITE).sum())
    exc_vert = int((df_dqo_f["DQO_vertimiento"] >= DQO_LIMITE).sum())
    col5, col6 = st.columns(2)
    n_dias = len(df_dqo_f)
    col5.metric("Días sobre límite — Reactor", f"{exc_reactor} / {n_dias} ({exc_reactor / n_dias * 100:.1f}%)")
    col6.metric("Días sobre límite — Vert.", f"{exc_vert} / {n_dias} ({exc_vert / n_dias * 100:.1f}%)")

    st.divider()

    # Gráfica de línea — ambos puntos en el mismo canvas
    fig_dqo_line = go.Figure()
    fig_dqo_line.add_trace(go.Scatter(
        x=df_dqo_f["fecha"], y=df_dqo_f["DQO_reactor_bio"],
        mode="lines+markers",
        line=dict(color=COLOR_REACTOR, width=2), marker=dict(size=5),
        name="Reactor Biológico",
    ))
    fig_dqo_line.add_trace(go.Scatter(
        x=df_dqo_f["fecha"], y=df_dqo_f["DQO_vertimiento"],
        mode="lines+markers",
        line=dict(color=COLOR_VERT, width=2), marker=dict(size=5),
        name="Vertimiento",
    ))
    fig_dqo_line.add_hline(
        y=DQO_LIMITE, line_dash="dash", line_color="red",
        annotation_text="Límite máx. Res. 0631/2015 (700 mg/L)",
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

    # Gráfica de barras agrupadas
    fig_dqo_bar = go.Figure()
    fig_dqo_bar.add_trace(go.Bar(
        x=df_dqo_f["fecha"], y=df_dqo_f["DQO_reactor_bio"],
        name="Reactor Biológico", marker_color=COLOR_REACTOR,
    ))
    fig_dqo_bar.add_trace(go.Bar(
        x=df_dqo_f["fecha"], y=df_dqo_f["DQO_vertimiento"],
        name="Vertimiento", marker_color=COLOR_VERT,
    ))
    fig_dqo_bar.add_hline(y=DQO_LIMITE, line_dash="dash", line_color="red")
    fig_dqo_bar.update_layout(
        barmode="group", height=280,
        margin=dict(l=20, r=20, t=10, b=40),
        xaxis=dict(tickformat="%d %b"),
        yaxis=dict(range=[100, 1100]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    st.plotly_chart(fig_dqo_bar, use_container_width=True)

    st.divider()

    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.markdown("**🟣 Reactor Biológico — Días ≥ 700 mg/L**")
        df_exc_reactor = df_dqo_f[df_dqo_f["DQO_reactor_bio"] >= DQO_LIMITE].copy()
        if df_exc_reactor.empty:
            st.success("Ningún día superó el límite en el Reactor Biológico.")
        else:
            df_show = df_exc_reactor[["fecha", "DQO_reactor_bio", "mes"]].copy()
            df_show["fecha"] = df_show["fecha"].dt.strftime("%d/%m/%Y")
            df_show.columns = ["Fecha", "DQO Reactor (mg/L)", "Mes"]
            st.dataframe(
                df_show.style.format({"DQO Reactor (mg/L)": "{:.1f}"}).set_properties(
                    **{"background-color": "#EDE7F6", "color": "#000000"}
                ),
                use_container_width=True, hide_index=True,
            )

    with col_t2:
        st.markdown("**🟠 Vertimiento — Días ≥ 700 mg/L (Res. 0631/2015)**")
        df_exc_vert_dqo = df_dqo_f[df_dqo_f["DQO_vertimiento"] >= DQO_LIMITE].copy()
        if df_exc_vert_dqo.empty:
            st.success("Ningún día superó el límite en el Vertimiento.")
        else:
            df_show = df_exc_vert_dqo[["fecha", "DQO_vertimiento", "mes"]].copy()
            df_show["fecha"] = df_show["fecha"].dt.strftime("%d/%m/%Y")
            df_show.columns = ["Fecha", "DQO Vertimiento (mg/L)", "Mes"]
            st.dataframe(
                df_show.style.format({"DQO Vertimiento (mg/L)": "{:.1f}"}).set_properties(
                    **{"background-color": "#FFCDD2", "color": "#000000"}
                ),
                use_container_width=True, hide_index=True,
            )

    st.divider()

    st.subheader("Tabla de valores — DQO")
    df_dqo_tabla = df_dqo_f[["fecha", "DQO_reactor_bio", "DQO_vertimiento", "mes"]].copy()
    df_dqo_tabla["fecha"] = df_dqo_tabla["fecha"].dt.strftime("%d/%m/%Y")
    df_dqo_tabla.columns = ["Fecha", "DQO Reactor Bio (mg/L)", "DQO Vertimiento (mg/L)", "Mes"]
    st.dataframe(
        df_dqo_tabla.style.format({
            "DQO Reactor Bio (mg/L)": "{:.1f}",
            "DQO Vertimiento (mg/L)": "{:.1f}",
        }),
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

    st.subheader("Mediciones de DQO — diarias")
    df_dqo_tabla2 = df_dqo_f[["fecha", "DQO_reactor_bio", "DQO_vertimiento", "mes"]].copy()
    df_dqo_tabla2["fecha"] = df_dqo_tabla2["fecha"].dt.strftime("%d/%m/%Y")
    df_dqo_tabla2.columns = ["Fecha", "DQO Reactor Bio (mg/L)", "DQO Vertimiento (mg/L)", "Mes"]
    st.dataframe(
        df_dqo_tabla2.style.format({
            "DQO Reactor Bio (mg/L)": "{:.1f}",
            "DQO Vertimiento (mg/L)": "{:.1f}",
        }),
        use_container_width=True, hide_index=True,
    )
