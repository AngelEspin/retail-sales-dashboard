"""
Dashboard de Ventas Minoristas 2023 — Grupo 2
Angel Espin · Carlos Ramirez
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Ventas Minoristas 2023 — Grupo 2", page_icon="📊", layout="wide")

COL_PALETTE = {"Beauty": "#4E79A7", "Clothing": "#F28E2B", "Electronics": "#59A14F"}
COL_GENDER = {"Female": "#E15759", "Male": "#4E79A7"}

CSV_PATH = Path(__file__).parent / "retail_sales_clean.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_PATH, parse_dates=["Date"])
    return df

df = load_data()

# SIDEBAR - FILTROS
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

# TITULO
st.markdown("<h1 style='text-align:center;'>Analisis Visual de Ventas Minoristas 2023</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:1.1em;'><b>Grupo 2</b> — Angel Espin & Carlos Ramirez</p>", unsafe_allow_html=True)
st.markdown("---")

# KPIs
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

# FILA 2 - Tendencia + Categoria
col1, col2 = st.columns(2)

with col1:
    st.subheader("Tendencia Mensual de Ingresos")
    orden_meses = ["01-Enero","02-Febrero","03-Marzo","04-Abril","05-Mayo","06-Junio",
                   "07-Julio","08-Agosto","09-Septiembre","10-Octubre","11-Noviembre","12-Diciembre"]
    monthly = dff.groupby("NombreMes", sort=False)["Total Amount"].sum()
    monthly = monthly.reindex([m for m in orden_meses if m in monthly.index]).dropna()

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=monthly.index, y=monthly.values,
        mode="lines+markers", line=dict(color="#4E79A7", width=3),
        marker=dict(size=8, color="#4E79A7"), name="Ingresos"))
    fig1.update_layout(xaxis_title="Mes", yaxis_title="Ingresos ($)", height=350, margin=dict(l=40,r=20,t=20,b=80))
    fig1.update_xaxes(tickangle=45)
    st.plotly_chart(fig1, use_container_width=True)

    if categoria_sel == "Todas":
        st.caption("Desglose por categoria:")
        cm = dff.groupby(["Product Category","NombreMes"])["Total Amount"].sum().reset_index()
        fig1b = px.line(cm, x="NombreMes", y="Total Amount", color="Product Category",
                        color_discrete_map=COL_PALETTE, markers=True)
        fig1b.update_layout(height=250, margin=dict(l=40,r=20,t=10,b=80), showlegend=True)
        fig1b.update_xaxes(tickangle=45)
        st.plotly_chart(fig1b, use_container_width=True)

with col2:
    st.subheader("Ingresos por Categoria")
    ca = dff.groupby("Product Category").agg(Ingresos=("Total Amount","sum"), Unidades=("Quantity","sum")).sort_values("Ingresos").reset_index()
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(y=ca["Product Category"], x=ca["Ingresos"], orientation="h",
        marker_color=[COL_PALETTE[c] for c in ca["Product Category"]],
        text=ca["Ingresos"].apply(lambda x: f"${x:,.0f}"), textposition="outside"))
    fig2.update_layout(xaxis_title="Ingresos ($)", yaxis_title="", height=300, margin=dict(l=10,r=20,t=20,b=40))
    st.plotly_chart(fig2, use_container_width=True)

    st.caption("Unidades por categoria:")
    cu = ca.sort_values("Unidades")
    fig2b = go.Figure()
    fig2b.add_trace(go.Bar(y=cu["Product Category"], x=cu["Unidades"], orientation="h",
        marker_color=[COL_PALETTE[c] for c in cu["Product Category"]],
        text=cu["Unidades"], textposition="outside"))
    fig2b.update_layout(xaxis_title="Unidades", yaxis_title="", height=250, margin=dict(l=10,r=20,t=10,b=40))
    st.plotly_chart(fig2b, use_container_width=True)

st.markdown("---")

# FILA 3 - Demografico + Mapa de calor
col3, col4 = st.columns(2)

with col3:
    st.subheader("Perfil Demografico: Ingresos por Edad y Genero")
    demo = dff.groupby(["GrupoEdad","Gender"])["Total Amount"].sum().reset_index()
    fig3 = go.Figure()
    for gen in ["Female","Male"]:
        sub = demo[demo["Gender"]==gen]
        fig3.add_trace(go.Bar(x=sub["GrupoEdad"], y=sub["Total Amount"], name=gen,
            marker_color=COL_GENDER[gen],
            text=sub["Total Amount"].apply(lambda x: f"${x:,.0f}"), textposition="outside"))
    fig3.update_layout(barmode="group", xaxis_title="Grupo de Edad", yaxis_title="Ingresos ($)",
                       height=400, margin=dict(l=40,r=20,t=20,b=40), legend_title="Genero")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Mapa de Calor: Categoria x Mes")
    heat = dff.pivot_table(index="Product Category", columns="NombreMes", values="Total Amount", aggfunc="sum")
    heat = heat[[c for c in orden_meses if c in heat.columns]]
    fig4 = px.imshow(heat.values, x=heat.columns, y=heat.index, text_auto=".0f",
                     color_continuous_scale="Blues", aspect="auto",
                     labels=dict(x="Mes", y="Categoria", color="Ingresos ($)"))
    fig4.update_layout(height=400, margin=dict(l=40,r=20,t=20,b=80))
    fig4.update_xaxes(tickangle=45)
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.markdown("<p style='text-align:center; color:gray; font-size:0.85em;'>"
    "Fuente: <i>Retail Sales Dataset</i> (Kaggle). Datos sinteticos, 2023.<br>"
    "Proyecto: Analisis Visual de Ventas Minoristas — Grupo 2</p>", unsafe_allow_html=True)

with st.expander("Ver datos filtrados"):
    st.dataframe(dff.drop(columns=["Customer ID","Transaction ID"]), use_container_width=True, hide_index=True)
