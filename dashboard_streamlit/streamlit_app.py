import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Retail Sales Dashboard 2023 — Grupo 2", layout="wide")

RAW_URL = "https://raw.githubusercontent.com/RISHIshrivas/Retail-Sales-data-analysis/main/retail_sales_dataset.csv"

MESES_LABEL = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
               7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}
MESES_SORT = {1:"01-Enero",2:"02-Febrero",3:"03-Marzo",4:"04-Abril",
              5:"05-Mayo",6:"06-Junio",7:"07-Julio",8:"08-Agosto",
              9:"09-Septiembre",10:"10-Octubre",11:"11-Noviembre",12:"12-Diciembre"}
DIAS = {0:"Lunes",1:"Martes",2:"Miercoles",3:"Jueves",4:"Viernes",5:"Sabado",6:"Domingo"}
ORDEN_MESES = list(MESES_SORT.values())

COL_CAT = {"Beauty":"#4E79A7","Clothing":"#F28E2B","Electronics":"#59A14F"}
COL_GEN = {"Female":"#E15759","Male":"#4E79A7"}
COL_DOW = ["#4E79A7","#5a8abf","#6d9bd4","#8aafe0","#a8c4ec","#e8a0a0","#d47c7c"]

@st.cache_data
def load_data():
    df = pd.read_csv(RAW_URL)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Anio"] = df["Date"].dt.year
    df["Mes"] = df["Date"].dt.month
    df["NombreMes"] = df["Mes"].map(MESES_SORT)
    df["MesLabel"] = df["Mes"].map(MESES_LABEL)
    df["Trimestre"] = "T" + df["Date"].dt.quarter.astype(str)
    df["DiaSemana"] = df["Date"].dt.dayofweek.map(DIAS)
    df["DiaNum"] = df["Date"].dt.dayofweek
    df["TipoDia"] = df["DiaNum"].apply(lambda d: "Fin de semana" if d >= 5 else "Entre semana")
    df["GrupoEdad"] = pd.cut(df["Age"], bins=[18,25,35,45,55,65],
                              labels=["18-25","26-35","36-45","46-55","56-65"],
                              include_lowest=True,right=True).astype(str)
    df["NivelPrecio"] = df["Price per Unit"].apply(lambda p: "Bajo (<=$50)" if p <= 50 else "Alto (>=$300)")
    return df

df = load_data()

st.sidebar.markdown("## Filtros")
trimestre_sel = st.sidebar.selectbox("Trimestre", ["Todos"] + sorted(df["Trimestre"].unique()))
genero_sel = st.sidebar.selectbox("Genero", ["Todos"] + sorted(df["Gender"].unique()))
categoria_sel = st.sidebar.selectbox("Categoria", ["Todas"] + sorted(df["Product Category"].unique()))
nivel_sel = st.sidebar.selectbox("Nivel de Precio", ["Todos"] + sorted(df["NivelPrecio"].unique()))

mask = pd.Series(True, index=df.index)
if trimestre_sel != "Todos": mask &= df["Trimestre"] == trimestre_sel
if genero_sel != "Todos": mask &= df["Gender"] == genero_sel
if categoria_sel != "Todas": mask &= df["Product Category"] == categoria_sel
if nivel_sel != "Todos": mask &= df["NivelPrecio"] == nivel_sel
dff = df[mask].copy()

st.markdown("""
<style>
.block-container { padding-top: 1.5rem; }
h1,h2,h3,h4 { font-family: 'Segoe UI', Arial, sans-serif; }
.kpi-card { background: #ffffff; border-radius: 12px; padding: 1rem 0.5rem; text-align: center; border-left: 4px solid #4E79A7; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.kpi-label { font-size: 0.75rem; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px; }
.kpi-value { font-size: 1.5rem; font-weight: 700; color: #1a2634; margin-top: 2px; }
.chart-card { background: #ffffff; border-radius: 12px; padding: 1rem 1rem 0.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 1rem; }
.section-title { font-size: 1.05rem; font-weight: 600; color: #1a2634; margin-bottom: 0.25rem; }
hr { margin: 1.5rem 0; opacity: 0.25; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; padding: 0.5rem 0 0.25rem;">
    <h1 style="font-size: 2.2rem; font-weight: 700; color: #1a2634; letter-spacing: -0.5px; margin:0;">
        Retail Sales Dashboard 2023
    </h1>
    <p style="font-size: 1rem; color: #6c757d; margin-top: 0.2rem;">
        Grupo 2 — Angel Espin · Carlos Ramirez &nbsp;|&nbsp;
        <span style="color:#4E79A7;">Analisis Visual de Ventas Minoristas</span>
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

tot_rev = dff["Total Amount"].sum()
tot_trans = len(dff)
avg_ticket = dff["Total Amount"].mean()
tot_units = dff["Quantity"].sum()
avg_age = dff["Age"].mean()
n_cats = dff["Product Category"].nunique()

kc = st.columns(6)
for i,(lbl,val) in enumerate(zip(
    ["Ingresos","Transacciones","Ticket Promedio","Unidades","Edad Promedio","Categorias"],
    [f"${tot_rev:,.0f}",f"{tot_trans:,}",f"${avg_ticket:,.2f}",f"{tot_units:,}",f"{avg_age:.1f} anos",str(n_cats)]
)):
    kc[i].markdown(f'<div class="kpi-card"><div class="kpi-label">{lbl}</div><div class="kpi-value">{val}</div></div>', unsafe_allow_html=True)

st.markdown("---")

c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Tendencia Mensual de Ingresos por Categoria</div>', unsafe_allow_html=True)
    mc = dff.groupby(["NombreMes","Product Category"])["Total Amount"].sum().reset_index()
    mc = mc[mc["NombreMes"].isin(ORDEN_MESES)]
    mc["_n"] = mc["NombreMes"].str[:2].astype(int)
    mc = mc.sort_values("_n")
    fig = px.area(mc, x="NombreMes", y="Total Amount", color="Product Category",
                  color_discrete_map=COL_CAT, line_shape="spline",
                  labels={"NombreMes":"","Total Amount":"","Product Category":""})
    fig.update_layout(height=370, legend=dict(orientation="h",y=1.02,x=0.5,xanchor="center"),
                      hovermode="x unified", margin=dict(t=20,b=20),
                      plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)")
    fig.update_yaxes(tickprefix="$", gridcolor="#e0e0e0", linecolor="#888", linewidth=1.2)
    fig.update_xaxes(gridcolor="#e0e0e0", linecolor="#888", linewidth=1.2)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Distribucion Jerarquica de Ingresos</div>', unsafe_allow_html=True)
    sd = dff.groupby(["Product Category","Gender","GrupoEdad"])["Total Amount"].sum().reset_index()
    fig = px.sunburst(sd, path=["Product Category","Gender","GrupoEdad"], values="Total Amount",
                      color="Product Category", color_discrete_map=COL_CAT)
    fig.update_layout(height=370, margin=dict(t=20,b=20),
                      plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)")
    fig.update_traces(textinfo="label+percent entry", textfont=dict(size=12))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

c3, c4 = st.columns(2)

with c3:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Ingresos por Grupo Etario y Genero</div>', unsafe_allow_html=True)
    demo = dff.groupby(["GrupoEdad","Gender"])["Total Amount"].sum().reset_index()
    fig = go.Figure()
    for gen in ["Female","Male"]:
        sub = demo[demo["Gender"]==gen]
        fig.add_trace(go.Bar(x=sub["GrupoEdad"], y=sub["Total Amount"], name=gen,
            marker_color=COL_GEN[gen],
            text=sub["Total Amount"].apply(lambda x: f"${x:,.0f}"),
            textposition="outside", textfont=dict(size=11),
            hovertemplate="%{x}<br>%{y:$,.0f}<extra>%{legend}</extra>"))
    fig.update_layout(barmode="group", height=370,
        legend=dict(orientation="h",y=1.02,x=0.5,xanchor="center"),
        hovermode="x unified", margin=dict(t=20,b=20),
        plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title=None), yaxis=dict(title="Ingresos ($)"))
    fig.update_xaxes(gridcolor="#e0e0e0", linecolor="#888", linewidth=1.2)
    fig.update_yaxes(tickprefix="$", gridcolor="#e0e0e0", linecolor="#888", linewidth=1.2)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c4:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Patrones de Compra: Precio vs Cantidad</div>', unsafe_allow_html=True)
    sd = dff.sample(min(500,len(dff)), random_state=42)
    fig = px.scatter(sd, x="Quantity", y="Price per Unit", color="Product Category",
        size="Total Amount", size_max=28, color_discrete_map=COL_CAT,
        labels={"Quantity":"Cantidad","Price per Unit":"Precio Unitario ($)","Product Category":""},
        hover_data={"Total Amount":":$,.0f","Quantity":True,"Price per Unit":True})
    fig.update_layout(height=370, legend=dict(orientation="h",y=1.02,x=0.5,xanchor="center"),
        hovermode="closest", margin=dict(t=20,b=20),
        plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)")
    fig.update_xaxes(gridcolor="#e0e0e0", dtick=1, linecolor="#888", linewidth=1.2)
    fig.update_yaxes(gridcolor="#e0e0e0", tickprefix="$", linecolor="#888", linewidth=1.2)
    fig.update_traces(marker=dict(line=dict(width=1,color="rgba(0,0,0,0.15)")))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

c5, c6 = st.columns(2)

with c5:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Mapa de Calor: Ingresos por Categoria y Mes</div>', unsafe_allow_html=True)
    hp = dff.groupby(["NombreMes","Product Category"])["Total Amount"].sum().reset_index()
    hp = hp[hp["NombreMes"].isin(ORDEN_MESES)]
    hp = hp.pivot(index="Product Category", columns="NombreMes", values="Total Amount")
    hp = hp[[c for c in ORDEN_MESES if c in hp.columns]].fillna(0)
    fig = go.Figure(data=go.Heatmap(
        z=hp.values, x=hp.columns, y=hp.index,
        text=hp.values, texttemplate="$%{text:,.0f}", textfont=dict(size=11),
        colorscale=[[0,"#f0f4f8"],[0.3,"#a8c4e0"],[0.6,"#4E79A7"],[1,"#1a3a5c"]],
        hovertemplate="%{y}<br>%{x}<br>$%{z:,.0f}<extra></extra>"))
    fig.update_layout(height=370, margin=dict(t=20,b=50),
        plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(side="bottom"), yaxis=dict(title=None))
    fig.update_xaxes(gridcolor="#e0e0e0", tickangle=45, linecolor="#888", linewidth=1.2)
    fig.update_yaxes(gridcolor="#e0e0e0", linecolor="#888", linewidth=1.2)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c6:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Actividad Semanal: Ingresos por Dia</div>', unsafe_allow_html=True)
    dow = dff.groupby("DiaNum").agg(Ingresos=("Total Amount","sum"), Transacciones=("Transaction ID","count")).reset_index()
    dow["DiaSemana"] = dow["DiaNum"].map(DIAS)
    dow = dow.sort_values("DiaNum")
    fig = go.Figure()
    fig.add_trace(go.Barpolar(
        r=dow["Ingresos"], theta=dow["DiaSemana"],
        marker=dict(color=[COL_DOW[int(i)] for i in dow["DiaNum"]]),
        text=dow["Ingresos"].apply(lambda x: f"${x:,.0f}"),
        textposition="outside", textfont=dict(size=11),
        hovertemplate="%{theta}<br>Ingresos: $%{r:,.0f}<br>Transacciones: %{customdata}<extra></extra>",
        customdata=dow["Transacciones"],
        width=0.7))
    fig.update_layout(height=370, margin=dict(t=20,b=20,r=40,l=40),
        polar=dict(radialaxis=dict(visible=True, tickprefix="$", gridcolor="#e0e0e0"),
                   angularaxis=dict(gridcolor="#e0e0e0")),
        plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#888; font-size:0.85rem; padding:0.5rem 0;">
    Fuente: <i>Retail Sales Dataset</i> (Kaggle) &nbsp;|&nbsp;
    Datos sinteticos 2023 &nbsp;|&nbsp;
    Proyecto Academico — Grupo 2
</div>
""", unsafe_allow_html=True)

with st.expander("Ver datos filtrados"):
    st.dataframe(dff.drop(columns=["Customer ID","Transaction ID"]), use_container_width=True, hide_index=True)
