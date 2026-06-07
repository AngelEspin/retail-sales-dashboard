import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Ventas Minoristas 2023 — Grupo 2", page_icon=":bar_chart:", layout="wide")

RAW_URL = "https://raw.githubusercontent.com/RISHIshrivas/Retail-Sales-data-analysis/main/retail_sales_dataset.csv"

MESES = {
    1:"01-Enero", 2:"02-Febrero", 3:"03-Marzo", 4:"04-Abril",
    5:"05-Mayo", 6:"06-Junio", 7:"07-Julio", 8:"08-Agosto",
    9:"09-Septiembre", 10:"10-Octubre", 11:"11-Noviembre", 12:"12-Diciembre",
}
DIAS = {
    0:"1-Lunes", 1:"2-Martes", 2:"3-Miercoles", 3:"4-Jueves",
    4:"5-Viernes", 5:"6-Sabado", 6:"7-Domingo",
}

COL_CAT = {"Beauty": "#4E79A7", "Clothing": "#F28E2B", "Electronics": "#59A14F"}
COL_GEN = {"Female": "#E15759", "Male": "#4E79A7"}
ORDEN_MESES = ["01-Enero","02-Febrero","03-Marzo","04-Abril","05-Mayo","06-Junio",
               "07-Julio","08-Agosto","09-Septiembre","10-Octubre","11-Noviembre","12-Diciembre"]

THEME_LAYOUT = dict(
    font=dict(family="Segoe UI, Arial, sans-serif", size=13),
    paper_bgcolor="#f5f5f5",
    plot_bgcolor="#f5f5f5",
    hovermode="x unified",
    dragmode=False,
)
AXIS_STYLE = dict(
    showline=True, linecolor="#d0d0d0", linewidth=1,
    gridcolor="#eaeaea", zerolinecolor="#e0e0e0",
    title_font=dict(size=13),
    tickfont=dict(size=12),
)

@st.cache_data
def load_data():
    df = pd.read_csv(RAW_URL)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Anio"] = df["Date"].dt.year
    df["Mes"] = df["Date"].dt.month
    df["NombreMes"] = df["Mes"].map(MESES)
    df["Trimestre"] = "T" + df["Date"].dt.quarter.astype(str)
    df["DiaSemana"] = df["Date"].dt.dayofweek.map(DIAS)
    df["TipoDia"] = df["Date"].dt.dayofweek.apply(lambda d: "Fin de semana" if d >= 5 else "Entre semana")
    df["GrupoEdad"] = pd.cut(df["Age"], bins=[18, 25, 35, 45, 55, 65],
                              labels=["18-25", "26-35", "36-45", "46-55", "56-65"],
                              include_lowest=True, right=True).astype(str)
    df["NivelPrecio"] = df["Price per Unit"].apply(lambda p: "Bajo (<=$50)" if p <= 50 else "Alto (>=$300)")
    return df

df = load_data()

st.sidebar.markdown("## Filtros")
trimestres = ["Todos"] + sorted(df["Trimestre"].unique())
trimestre_sel = st.sidebar.selectbox("Trimestre", trimestres, key="tri")
generos = ["Todos"] + sorted(df["Gender"].unique())
genero_sel = st.sidebar.selectbox("Genero", generos, key="gen")
categorias = ["Todas"] + sorted(df["Product Category"].unique())
categoria_sel = st.sidebar.selectbox("Categoria", categorias, key="cat")

mask = pd.Series(True, index=df.index)
if trimestre_sel != "Todos":
    mask &= df["Trimestre"] == trimestre_sel
if genero_sel != "Todos":
    mask &= df["Gender"] == genero_sel
if categoria_sel != "Todas":
    mask &= df["Product Category"] == categoria_sel
dff = df[mask].copy()

st.markdown("<h1 style='text-align:center; font-weight:500; letter-spacing:-0.5px;'>Visualizacion de Ventas Minoristas 2023</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:1.05rem; color:#555;'>Grupo 2 — Angel Espin & Carlos Ramirez</p>", unsafe_allow_html=True)
st.markdown("---")

ingresos = int(dff["Total Amount"].sum())
n_trans = len(dff)
ticket = round(dff["Total Amount"].mean(), 2)
unidades = int(dff["Quantity"].sum())

k1, k2, k3, k4 = st.columns(4)
k1.metric("Ingresos Totales", f"${ingresos:,}")
k2.metric("Transacciones", f"{n_trans:,}")
k3.metric("Ticket Promedio", f"${ticket:,.2f}")
k4.metric("Unidades Vendidas", f"{unidades:,}")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Tendencia Mensual de Ingresos")
    monthly = dff.groupby("NombreMes", sort=False)["Total Amount"].sum()
    monthly = monthly.reindex([m for m in ORDEN_MESES if m in monthly.index]).dropna()
    avg_monthly = monthly.mean()

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=monthly.index, y=monthly.values,
        mode="lines+markers",
        line=dict(color="#2c5f8a", width=3),
        marker=dict(size=9, color="#2c5f8a", line=dict(color="white", width=1)),
        name="Ingresos",
        hovertemplate="%{x}<br>%{y:$,.0f}<extra></extra>",
    ))
    fig1.add_hline(y=avg_monthly, line=dict(color="#999", width=1.5, dash="dash"),
                   annotation_text=f"Promedio ${avg_monthly:,.0f}", annotation_position="bottom right")
    fig1.update_layout(**THEME_LAYOUT, title=None, xaxis_title=None, yaxis_title="Ingresos ($)", height=320, margin=dict(l=16, r=16, t=40, b=64))
    fig1.update_xaxes(**AXIS_STYLE, tickangle=45)
    fig1.update_yaxes(**AXIS_STYLE, tickprefix="$", separatethousands=True)
    st.plotly_chart(fig1, use_container_width=True)

    cats_visibles = sorted(dff["Product Category"].unique())
    if not cats_visibles:
        st.caption("Sin datos para los filtros seleccionados")
    else:
        if categoria_sel == "Todas":
            titulo_breakdown = "Desglose por categoria"
        else:
            titulo_breakdown = f"Tendencia: {categoria_sel}"
        st.caption(titulo_breakdown)
        cm = dff.groupby(["Product Category", "NombreMes"])["Total Amount"].sum().reset_index()
        fig1b = go.Figure()
        for cat in ["Beauty", "Clothing", "Electronics"]:
            if cat not in cats_visibles:
                continue
            sub = cm[cm["Product Category"] == cat]
            fig1b.add_trace(go.Scatter(
                x=sub["NombreMes"], y=sub["Total Amount"],
                mode="lines+markers",
                name=cat,
                line=dict(color=COL_CAT[cat], width=2.5),
                marker=dict(size=7, color=COL_CAT[cat], line=dict(color="white", width=1)),
                hovertemplate="%{x}<br>%{y:$,.0f}<extra>%{legend}</extra>",
            ))
        fig1b.update_layout(**THEME_LAYOUT, title=None, height=220, showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            margin=dict(l=16, r=16, t=10, b=48))
        fig1b.update_xaxes(**AXIS_STYLE, tickangle=45)
        fig1b.update_yaxes(**AXIS_STYLE, tickprefix="$", separatethousands=True)
        st.plotly_chart(fig1b, use_container_width=True)

with col2:
    st.subheader("Ingresos por Categoria")
    ca = dff.groupby("Product Category").agg(
        Ingresos=("Total Amount", "sum"),
        Unidades=("Quantity", "sum"),
        Ticket=("Total Amount", "mean"),
    ).sort_values("Ingresos").reset_index()
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        y=ca["Product Category"], x=ca["Ingresos"], orientation="h",
        marker_color=[COL_CAT[c] for c in ca["Product Category"]],
        text=ca["Ingresos"].apply(lambda x: f"${x:,.0f}"),
        textposition="outside",
        hovertemplate="%{y}<br>%{x:$,.0f}<extra></extra>",
    ))
    fig2.update_layout(**THEME_LAYOUT, title=None, xaxis_title=None, yaxis_title=None,
                       height=260, xaxis=dict(visible=False), margin=dict(l=16, r=16, t=40, b=48))
    fig2.update_yaxes(**AXIS_STYLE)
    fig2.update_traces(textfont_size=13, textangle=0)
    st.plotly_chart(fig2, use_container_width=True)

    st.caption("Precio vs Cantidad por transaccion")
    scatter = dff.sample(min(500, len(dff)), random_state=42)
    fig2b = go.Figure()
    for cat in ["Beauty", "Clothing", "Electronics"]:
        sub = scatter[scatter["Product Category"] == cat]
        fig2b.add_trace(go.Scatter(
            x=sub["Quantity"], y=sub["Price per Unit"],
            mode="markers",
            name=cat,
            marker=dict(
                color=COL_CAT[cat], size=sub["Total Amount"] / sub["Total Amount"].max() * 30 + 6,
                line=dict(color="rgba(0,0,0,0.15)", width=1),
                opacity=0.75,
            ),
            hovertemplate="<b>%{text}</b><br>Cantidad: %{x}<br>Precio: $%{y:.0f}<br>Total: $%{customdata:,.0f}<extra></extra>",
            text=sub["Product Category"],
            customdata=sub["Total Amount"],
        ))
    fig2b.update_layout(**THEME_LAYOUT, title=None, height=240, showlegend=True,
                        xaxis_title="Cantidad", yaxis_title="Precio por Unidad ($)",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                        margin=dict(l=16, r=16, t=10, b=48))
    fig2b.update_xaxes(**AXIS_STYLE, dtick=1)
    fig2b.update_yaxes(**AXIS_STYLE, tickprefix="$")
    st.plotly_chart(fig2b, use_container_width=True)

st.markdown("---")

col3, col4 = st.columns(2)

with col3:
    st.subheader("Ingresos por Grupo de Edad y Genero")
    demo = dff.groupby(["GrupoEdad", "Gender"])["Total Amount"].sum().reset_index()
    fig3 = go.Figure()
    for gen in ["Female", "Male"]:
        sub = demo[demo["Gender"] == gen]
        fig3.add_trace(go.Bar(
            x=sub["GrupoEdad"], y=sub["Total Amount"], name=gen,
            marker_color=COL_GEN[gen],
            text=sub["Total Amount"].apply(lambda x: f"${x:,.0f}"),
            textposition="outside",
            hovertemplate="%{x}<br>%{y:$,.0f}<extra>%{legend}</extra>",
        ))
    fig3.update_layout(**THEME_LAYOUT, barmode="group", title=None, xaxis_title=None,
                       yaxis_title="Ingresos ($)", height=380,
                       legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                       margin=dict(l=16, r=16, t=40, b=64))
    fig3.update_xaxes(**AXIS_STYLE)
    fig3.update_yaxes(**AXIS_STYLE, tickprefix="$", separatethousands=True)
    fig3.update_traces(textfont_size=11)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Mapa de Calor: Ingresos por Categoria y Mes")
    heat = dff.pivot_table(index="Product Category", columns="NombreMes", values="Total Amount", aggfunc="sum")
    heat = heat[[c for c in ORDEN_MESES if c in heat.columns]]
    fig4 = go.Figure(data=go.Heatmap(
        z=heat.values,
        x=heat.columns,
        y=heat.index,
        text=heat.values,
        texttemplate="$%{text:,.0f}",
        textfont=dict(size=11),
        colorscale=[[0, "#e8f0fe"], [0.5, "#4E79A7"], [1, "#1a3a5c"]],
        hovertemplate="%{y}<br>%{x}<br>$%{z:,.0f}<extra></extra>",
    ))
    fig4.update_layout(**THEME_LAYOUT, title=None, height=380,
                       xaxis=dict(side="bottom"), yaxis=dict(title=None),
                       margin=dict(l=16, r=16, t=40, b=64))
    fig4.update_xaxes(**AXIS_STYLE, tickangle=45)
    fig4.update_yaxes(**AXIS_STYLE)
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.markdown("<p style='text-align:center; color:#888; font-size:0.85rem;'>"
    "Fuente: <i>Retail Sales Dataset</i> (Kaggle) &nbsp;|&nbsp; "
    "Proyecto: Analisis Visual de Ventas Minoristas — Grupo 2</p>", unsafe_allow_html=True)

with st.expander("Ver datos filtrados"):
    st.dataframe(dff.drop(columns=["Customer ID", "Transaction ID"]), use_container_width=True, hide_index=True)
