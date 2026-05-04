import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from data import generar_datos

st.set_page_config(
    page_title="Dashboard PTAR D'Vida — pH y DQO",
    page_icon="💧",
    layout="wide",
)

PH_MIN = 6.0
PH_MAX = 9.0
DQO_LIMITE = 700.0  # Resolución 0631/2015

st.title("💧 Dashboard PTAR — pH y DQO")
st.markdown("Monitoreo diario de parámetros de calidad de agua ·  2026")
st.divider()

df = generar_datos()

with st.sidebar:
    st.header("Filtros")
    mes_sel = st.selectbox("Mes", ["Todos", "Mayo 2026", "Junio 2026"])

df_filtrado = df[df["mes"] == mes_sel].reset_index(drop=True) if mes_sel != "Todos" else df.copy()

# --- Métricas ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("pH Máximo", f"{df_filtrado['pH'].max():.2f}")
col2.metric("pH Mínimo", f"{df_filtrado['pH'].min():.2f}")
col3.metric("DQO Máximo (mg/L)", f"{df_filtrado['DQO_mg_L'].max():.1f}")
col4.metric("DQO Mínimo (mg/L)", f"{df_filtrado['DQO_mg_L'].min():.1f}")

st.divider()

# ============================================================
# SECCIÓN pH
# ============================================================
st.subheader("pH")

# Línea temporal pH
fig_ph_line = go.Figure()
fig_ph_line.add_trace(go.Scatter(
    x=df_filtrado["fecha"],
    y=df_filtrado["pH"],
    mode="lines+markers",
    line=dict(color="#2196F3", width=2),
    marker=dict(size=5),
    name="pH",
))
fig_ph_line.add_hline(
    y=PH_MIN, line_dash="dash", line_color="orange",
    annotation_text="Mínimo (6.0)", annotation_position="bottom right",
)
fig_ph_line.add_hline(
    y=PH_MAX, line_dash="dash", line_color="red",
    annotation_text="Máximo (9.0)", annotation_position="top right",
)
fig_ph_line.update_layout(
    xaxis=dict(title="Fecha", tickformat="%d %b"),
    yaxis=dict(title="pH", range=[5.0, 10.0]),
    hovermode="x unified",
    height=340,
    margin=dict(l=40, r=40, t=20, b=40),
    showlegend=False,
)
st.plotly_chart(fig_ph_line, use_container_width=True)

# Barras pH
fig_ph_bar = px.bar(
    df_filtrado, x="fecha", y="pH",
    color_discrete_sequence=["#2196F3"],
    labels={"fecha": "Fecha", "pH": "pH"},
)
fig_ph_bar.add_hline(y=PH_MIN, line_dash="dash", line_color="orange")
fig_ph_bar.add_hline(y=PH_MAX, line_dash="dash", line_color="red")
fig_ph_bar.update_layout(
    height=260, margin=dict(l=20, r=20, t=10, b=40),
    xaxis=dict(tickformat="%d %b"), yaxis=dict(range=[5.0, 10.0]),
)
st.plotly_chart(fig_ph_bar, use_container_width=True)

# Tablas de excedencias pH
df_ph_inf = df_filtrado[df_filtrado["pH"] <= PH_MIN].copy()
df_ph_sup = df_filtrado[df_filtrado["pH"] >= PH_MAX].copy()

col_t1, col_t2 = st.columns(2)

with col_t1:
    st.markdown("**⚠️ Días con pH ≤ 6.0 — límite inferior**")
    if df_ph_inf.empty:
        st.success("Sin excedencias del límite inferior.")
    else:
        df_show = df_ph_inf[["fecha", "pH", "mes"]].copy()
        df_show["fecha"] = df_show["fecha"].dt.strftime("%d/%m/%Y")
        df_show.columns = ["Fecha", "pH", "Mes"]
        styled = df_show.style.format({"pH": "{:.2f}"}).set_properties(
            **{"background-color": "#FFF176", "color": "#000000"}
        )
        st.dataframe(styled, use_container_width=True, hide_index=True)

with col_t2:
    st.markdown("**🔴 Días con pH ≥ 9.0 — límite superior**")
    if df_ph_sup.empty:
        st.success("Sin excedencias del límite superior.")
    else:
        df_show = df_ph_sup[["fecha", "pH", "mes"]].copy()
        df_show["fecha"] = df_show["fecha"].dt.strftime("%d/%m/%Y")
        df_show.columns = ["Fecha", "pH", "Mes"]
        styled = df_show.style.format({"pH": "{:.2f}"}).set_properties(
            **{"background-color": "#FFCDD2", "color": "#000000"}
        )
        st.dataframe(styled, use_container_width=True, hide_index=True)

st.divider()

# ============================================================
# SECCIÓN DQO
# ============================================================
st.subheader("DQO (mg/L)")

# Línea temporal DQO
fig_dqo_line = go.Figure()
fig_dqo_line.add_trace(go.Scatter(
    x=df_filtrado["fecha"],
    y=df_filtrado["DQO_mg_L"],
    mode="lines+markers",
    line=dict(color="#FF5722", width=2),
    marker=dict(size=5),
    name="DQO",
))
fig_dqo_line.add_hline(
    y=DQO_LIMITE, line_dash="dash", line_color="red",
    annotation_text="Límite máx. Res. 0631/2015 (700 mg/L)",
    annotation_position="top right",
)
fig_dqo_line.update_layout(
    xaxis=dict(title="Fecha", tickformat="%d %b"),
    yaxis=dict(title="DQO (mg/L)", range=[100, 1100]),
    hovermode="x unified",
    height=340,
    margin=dict(l=40, r=40, t=20, b=40),
    showlegend=False,
)
st.plotly_chart(fig_dqo_line, use_container_width=True)

# Barras DQO
fig_dqo_bar = px.bar(
    df_filtrado, x="fecha", y="DQO_mg_L",
    color_discrete_sequence=["#FF5722"],
    labels={"fecha": "Fecha", "DQO_mg_L": "DQO (mg/L)"},
)
fig_dqo_bar.add_hline(y=DQO_LIMITE, line_dash="dash", line_color="red")
fig_dqo_bar.update_layout(
    height=260, margin=dict(l=20, r=20, t=10, b=40),
    xaxis=dict(tickformat="%d %b"), yaxis=dict(range=[100, 1100]),
)
st.plotly_chart(fig_dqo_bar, use_container_width=True)

# Tabla excedencias DQO
st.markdown("**🔴 Días con DQO ≥ 700 mg/L — Resolución 0631/2015**")
df_dqo_sup = df_filtrado[df_filtrado["DQO_mg_L"] >= DQO_LIMITE].copy()

if df_dqo_sup.empty:
    st.success("Ningún día superó el límite de 700 mg/L.")
else:
    df_show = df_dqo_sup[["fecha", "DQO_mg_L", "mes"]].copy()
    df_show["fecha"] = df_show["fecha"].dt.strftime("%d/%m/%Y")
    df_show.columns = ["Fecha", "DQO (mg/L)", "Mes"]
    styled = df_show.style.format({"DQO (mg/L)": "{:.1f}"}).set_properties(
        **{"background-color": "#FFCDD2", "color": "#000000"}
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)

st.divider()

# --- Tabla completa de datos ---
st.subheader("Datos diarios")
df_tabla = df_filtrado.copy()
df_tabla["fecha"] = df_tabla["fecha"].dt.strftime("%d/%m/%Y")
df_tabla.columns = ["Fecha", "pH", "DQO (mg/L)", "Mes"]
st.dataframe(
    df_tabla.style.format({"pH": "{:.2f}", "DQO (mg/L)": "{:.1f}"}),
    use_container_width=True,
    hide_index=True,
)
