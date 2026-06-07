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
ORDEN_DIAS = ["Lunes","Martes","Miercoles","Jueves","Viernes","Sabado","Domingo"]

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

st.sidebar.markdown("""
<div style="background:#2c5f8a; color:white; padding:0.6rem 1rem; border-radius:8px; margin-bottom:1rem; text-align:center; font-weight:600; font-size:0.95rem;">
    Filtros del Dashboard
</div>
""", unsafe_allow_html=True)
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
.block-container { padding-top: 1rem; }
h1,h2,h3,h4 { font-family: 'Segoe UI', Arial, sans-serif; }

.main-header {
    background: linear-gradient(135deg, #1a2634 0%, #2c5f8a 100%);
    padding: 1.2rem 1.5rem 1rem;
    border-radius: 14px;
    text-align: center;
    margin-bottom: 1rem;
    box-shadow: 0 4px 12px rgba(26,38,52,0.15);
}
.main-header h1 { color: white; font-size: 1.9rem; margin: 0; font-weight: 600; letter-spacing: -0.3px; }
.main-header p { color: rgba(255,255,255,0.8); margin: 0.2rem 0 0; font-size: 0.95rem; }
.main-header span { color: #f2c94c; }

[data-testid="stSidebar"] { background-color: #f7f8fa; border-right: 1px solid #e8e8e8; }
[data-testid="stSidebar"] .sidebar-content { padding-top: 0.5rem; }

.kpi-row { margin-bottom: 1.2rem; }
.kpi-card {
    background:#ffffff; border-radius:10px; padding:0.8rem 0.3rem;
    text-align:center; box-shadow:0 2px 6px rgba(0,0,0,0.05);
    border-top: 3px solid #4E79A7; transition: transform 0.15s;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.kpi-label { font-size:0.7rem; color:#888; text-transform:uppercase; letter-spacing:0.4px; }
.kpi-value { font-size:1.4rem; font-weight:700; color:#1a2634; margin-top:1px; }

.chart-card {
    background:#ffffff; border-radius:10px; padding:0.8rem 0.8rem 0.3rem;
    box-shadow:0 2px 8px rgba(0,0,0,0.06); margin-bottom:0.8rem;
    border: 1px solid #f0f0f0;
}
.section-title { font-size:1rem; font-weight:600; color:#1a2634; margin-bottom:0.15rem; padding-left: 0.3rem; border-left: 3px solid #4E79A7; }

.stTabs [data-baseweb="tab-list"] { gap: 0; border-bottom: 2px solid #e8e8e8; }
.stTabs [data-baseweb="tab"] {
    font-weight: 500; height: auto; padding: 0.6rem 1.2rem;
    border-bottom: 2px solid transparent; margin-bottom: -2px;
}
.stTabs [aria-selected="true"] {
    color: #2c5f8a !important; border-bottom-color: #2c5f8a !important;
}

.stCaption { color: #777; font-size: 0.82rem; padding-left: 0.3rem; }
hr { margin:1.2rem 0; opacity:0.2; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>Retail Sales Dashboard 2023</h1>
    <p>Grupo 2 — Angel Espin · Carlos Ramirez &nbsp;|&nbsp; <span>Analisis Visual de Ventas Minoristas</span></p>
</div>
""", unsafe_allow_html=True)

tot_rev = dff["Total Amount"].sum()
tot_trans = len(dff)
avg_ticket = dff["Total Amount"].mean()
tot_units = dff["Quantity"].sum()
avg_age = dff["Age"].mean()
n_cats = dff["Product Category"].nunique()

KC = ["#2c5f8a","#59A14F","#F28E2B","#E15759","#4E79A7","#B07AA1"]
kc = st.columns(6)
for i,(lbl,val) in enumerate(zip(
    ["Ingresos","Transacciones","Ticket Promedio","Unidades","Edad Promedio","Categorias"],
    [f"${tot_rev:,.0f}",f"{tot_trans:,}",f"${avg_ticket:,.2f}",f"{tot_units:,}",f"{avg_age:.1f} anos",str(n_cats)]
)):
    kc[i].markdown(f'<div class="kpi-card" style="border-top-color:{KC[i]}"><div class="kpi-label">{lbl}</div><div class="kpi-value">{val}</div></div>', unsafe_allow_html=True)

st.markdown(f"""
<div style="text-align:right; font-size:0.8rem; color:#999; margin: -0.5rem 0 0.5rem;">
    Datos: {df['Date'].min().date()} a {df['Date'].max().date()}
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["Resumen General", "Demografia y Producto", "Analisis Temporal", "Perfil del Cliente"])

with tab1:
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
        fig.update_layout(height=380, legend=dict(orientation="h",y=1.02,x=0.5,xanchor="center"),
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
        fig.update_layout(height=380, margin=dict(t=20,b=20),
                          plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)")
        fig.update_traces(textinfo="label+percent entry", textfont=dict(size=12))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.caption("El area apilada muestra la evolucion mensual de ingresos desglosada por categoria. "
               "El sunburst revela la composicion jerarquica: categoria → genero → grupo etario, "
               "permitiendo identificar que segmentos concentran mayores ingresos.")

with tab2:
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
        fig.update_layout(barmode="group", height=380,
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
        sd["Count"] = 1
        ag = sd.groupby(["Product Category","Quantity","Price per Unit"], as_index=False).agg(Transacciones=("Count","sum"), Monto=("Total Amount","sum"))
        fig = px.scatter(ag, x="Quantity", y="Price per Unit", color="Product Category",
            size="Transacciones", size_max=30, color_discrete_map=COL_CAT,
            facet_col="Product Category", facet_col_wrap=3,
            labels={"Quantity":"Cantidad","Price per Unit":"Precio ($)","Product Category":""},
            hover_data={"Transacciones":True,"Monto":":$,.0f"})
        fig.update_layout(height=340, showlegend=False,
            margin=dict(t=10,b=20,l=0,r=0),
            plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)")
        fig.update_xaxes(gridcolor="#e0e0e0", dtick=1, linecolor="#888", linewidth=1.2)
        fig.update_yaxes(gridcolor="#e0e0e0", tickprefix="$", linecolor="#888", linewidth=1.2, range=[0,550])
        fig.update_traces(marker=dict(line=dict(width=1,color="white")))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    c3b, c4b = st.columns(2)
    with c3b:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Distribucion de Ingresos por Genero</div>', unsafe_allow_html=True)
        gr = dff.groupby("Gender")["Total Amount"].sum().reset_index()
        fig = px.pie(gr, values="Total Amount", names="Gender", color="Gender",
                     color_discrete_map=COL_GEN, hole=0.45)
        fig.update_traces(textinfo="label+percent+value", texttemplate="%{label}<br>$%{value:,.0f}<br>(%{percent})")
        fig.update_layout(height=280, margin=dict(t=10,b=10), showlegend=False,
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c4b:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Ingresos por Nivel de Precio</div>', unsafe_allow_html=True)
        nl = dff.groupby("NivelPrecio")["Total Amount"].sum().reset_index()
        nl_col = {"Bajo (<=$50)": "#59A14F", "Alto (>=$300)": "#E15759"}
        fig = px.bar(nl, x="NivelPrecio", y="Total Amount", color="NivelPrecio",
                     color_discrete_map=nl_col, text_auto="$,.0f")
        fig.update_layout(height=280, margin=dict(t=10,b=10), showlegend=False,
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          xaxis=dict(title=None), yaxis=dict(title=""))
        fig.update_yaxes(tickprefix="$", gridcolor="#e0e0e0", linecolor="#888", linewidth=1.2)
        fig.update_xaxes(gridcolor="#e0e0e0", linecolor="#888", linewidth=1.2)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.caption("Las barras agrupadas comparan ingresos por genero dentro de cada grupo etario. "
               "Cada categoria tiene su propio panel de precio vs cantidad, el tamano de la burbuja "
               "refleja la cantidad de transacciones en cada combinacion. El donut y la barra de nivel "
               "de precio complementan la vision: la brecha por genero es minima y los productos de "
               "precio alto (>=$300) concentran mas ingresos que los economicos.")

with tab3:
    c5, c6 = st.columns(2)
    with c5:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Distribucion de Ingresos: Categoria y Mes</div>', unsafe_allow_html=True)
        tm = dff.groupby(["Product Category","MesLabel"])["Total Amount"].sum().reset_index()
        tm = tm[tm["MesLabel"].isin(list(MESES_LABEL.values()))]
        tm["_n"] = tm["MesLabel"].map({v:k for k,v in MESES_LABEL.items()})
        tm = tm.sort_values("_n")
        fig = px.treemap(tm, path=["Product Category","MesLabel"], values="Total Amount",
                         color="Product Category", color_discrete_map=COL_CAT)
        fig.update_traces(textinfo="label+value", texttemplate="%{label}<br>$%{value:,.0f}",
                          hovertemplate="%{label}<br>$%{value:,.0f}<extra></extra>",
                          textfont=dict(size=11))
        fig.update_layout(height=380, margin=dict(t=20,b=20),
            plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c6:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Actividad Semanal: Ingresos por Dia</div>', unsafe_allow_html=True)
        dow = dff.groupby("DiaNum").agg(Ingresos=("Total Amount","sum"), Transacciones=("Transaction ID","count")).reset_index()
        dow = dow.sort_values("DiaNum")
        dow["DiaSemana"] = dow["DiaNum"].map(DIAS)
        fig = go.Figure()
        for _, row in dow.iterrows():
            fig.add_trace(go.Bar(
                x=[row["DiaSemana"]], y=[row["Ingresos"]],
                name=row["DiaSemana"],
                marker_color=COL_DOW[int(row["DiaNum"])],
                text=f"${row['Ingresos']:,.0f}",
                textposition="outside",
                textfont=dict(size=11),
                hovertemplate="%{x}<br>Ingresos: $%{y:,.0f}<br>Transacciones: %{customdata}<extra></extra>",
                customdata=[row["Transacciones"]],
                width=0.6,
            ))
        fig.update_layout(barmode="group", height=380,
            hovermode="x unified", margin=dict(t=20,b=40),
            plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title=None), yaxis=dict(title="Ingresos ($)"),
            showlegend=False)
        fig.update_xaxes(gridcolor="#e0e0e0", linecolor="#888", linewidth=1.2)
        fig.update_yaxes(tickprefix="$", gridcolor="#e0e0e0", linecolor="#888", linewidth=1.2)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    c5b, c6b = st.columns(2)
    with c5b:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Ingresos por Trimestre</div>', unsafe_allow_html=True)
        tq = dff.groupby(["Trimestre","Product Category"])["Total Amount"].sum().reset_index()
        tq = tq[tq["Trimestre"].isin(["T1","T2","T3","T4"])]
        fig = px.bar(tq, x="Trimestre", y="Total Amount", color="Product Category",
                     color_discrete_map=COL_CAT, text_auto="$,.0f",
                     barmode="relative", category_orders={"Trimestre":["T1","T2","T3","T4"]})
        fig.update_layout(height=280, margin=dict(t=10,b=10),
                          legend=dict(orientation="h",y=1.02,x=0.5,xanchor="center"),
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          xaxis=dict(title=None), yaxis=dict(title=""))
        fig.update_yaxes(tickprefix="$", gridcolor="#e0e0e0", linecolor="#888", linewidth=1.2)
        fig.update_xaxes(gridcolor="#e0e0e0", linecolor="#888", linewidth=1.2)
        fig.update_traces(textfont_size=10)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c6b:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Ticket Promedio por Dia</div>', unsafe_allow_html=True)
        td = dff.groupby("DiaNum").agg(Ticket=("Total Amount","mean"), Transacciones=("Transaction ID","count")).reset_index()
        td = td.sort_values("DiaNum")
        td["DiaSemana"] = td["DiaNum"].map(DIAS)
        fig = px.bar(td, x="DiaSemana", y="Ticket", color="DiaSemana",
                     color_discrete_map={d:c for d,c in zip(ORDEN_DIAS,COL_DOW)},
                     text_auto="$,.2f", category_orders={"DiaSemana":ORDEN_DIAS})
        fig.update_traces(hovertemplate="%{x}<br>Ticket: $%{y:,.2f}<br>Transacciones: %{customdata}<extra></extra>",
                          customdata=td["Transacciones"])
        fig.update_layout(height=280, margin=dict(t=10,b=10), showlegend=False,
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          xaxis=dict(title=None), yaxis=dict(title=""))
        fig.update_yaxes(tickprefix="$", gridcolor="#e0e0e0", linecolor="#888", linewidth=1.2)
        fig.update_xaxes(gridcolor="#e0e0e0", linecolor="#888", linewidth=1.2)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.caption("El treemap muestra el peso relativo de cada combinacion categoria-mes. "
               "Los trimestres agrupan la estacionalidad: T1 supera a los demas. "
               "El ticket por dia confirma que Sabado y Lunes tienen el gasto promedio mas alto.")

with tab4:
    c7, c8 = st.columns(2)
    with c7:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Distribucion de Edad de los Clientes</div>', unsafe_allow_html=True)
        fig = px.histogram(dff, x="Age", nbins=20, color_discrete_sequence=["#4E79A7"],
                           labels={"Age":"Edad","count":"Clientes"})
        fig.update_layout(height=280, margin=dict(t=10,b=10),
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          xaxis=dict(title=None), yaxis=dict(title=""))
        fig.update_xaxes(gridcolor="#e0e0e0", linecolor="#888", linewidth=1.2, dtick=5)
        fig.update_yaxes(gridcolor="#e0e0e0", linecolor="#888", linewidth=1.2)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c8:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Categoria Preferida por Genero</div>', unsafe_allow_html=True)
        cg = dff.groupby(["Gender","Product Category"]).agg(Transacciones=("Transaction ID","count"), Ingresos=("Total Amount","sum")).reset_index()
        fig = px.bar(cg, x="Gender", y="Transacciones", color="Product Category",
                     color_discrete_map=COL_CAT, text_auto=True, barmode="group",
                     labels={"Gender":"","Product Category":"","Transacciones":""})
        fig.update_layout(height=280, margin=dict(t=10,b=10),
                          legend=dict(orientation="h",y=1.02,x=0.5,xanchor="center"),
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          xaxis=dict(title=None), yaxis=dict(title=""))
        fig.update_xaxes(gridcolor="#e0e0e0", linecolor="#888", linewidth=1.2)
        fig.update_yaxes(gridcolor="#e0e0e0", linecolor="#888", linewidth=1.2)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    c9, c10 = st.columns(2)
    with c9:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Preferencia de Categoria por Grupo Etario</div>', unsafe_allow_html=True)
        ae = dff.groupby(["GrupoEdad","Product Category"])["Total Amount"].sum().reset_index()
        fig = px.bar(ae, x="GrupoEdad", y="Total Amount", color="Product Category",
                     color_discrete_map=COL_CAT, text_auto="$,.0f", barmode="relative",
                     category_orders={"GrupoEdad":["18-25","26-35","36-45","46-55","56-65"]})
        fig.update_layout(height=280, margin=dict(t=10,b=10),
                          legend=dict(orientation="h",y=1.02,x=0.5,xanchor="center"),
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          xaxis=dict(title=None), yaxis=dict(title=""))
        fig.update_yaxes(tickprefix="$", gridcolor="#e0e0e0", linecolor="#888", linewidth=1.2)
        fig.update_xaxes(gridcolor="#e0e0e0", linecolor="#888", linewidth=1.2)
        fig.update_traces(textfont_size=9)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c10:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Volumen de Transacciones por Categoria</div>', unsafe_allow_html=True)
        vc = dff["Product Category"].value_counts().reset_index()
        vc.columns = ["Categoria","Transacciones"]
        fig = px.bar(vc, x="Categoria", y="Transacciones", color="Categoria",
                     color_discrete_map=COL_CAT, text_auto=True)
        fig.update_layout(height=280, margin=dict(t=10,b=10), showlegend=False,
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          xaxis=dict(title=None), yaxis=dict(title=""))
        fig.update_xaxes(gridcolor="#e0e0e0", linecolor="#888", linewidth=1.2)
        fig.update_yaxes(gridcolor="#e0e0e0", linecolor="#888", linewidth=1.2)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.caption("La edad se distribuye uniformemente entre 18 y 64. "
               "Clothing es la categoria mas popular en ambos generos. "
               "El gasto por grupo etario muestra que 26-35 y 46-55 concentran los mayores ingresos "
               "en todas las categorias.")

st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#aaa; font-size:0.8rem; padding:0.5rem 0;">
    <span style="color:#4E79A7;">Retail Sales Dataset</span> (Kaggle) &nbsp;·&nbsp;
    Datos sinteticos 2023 &nbsp;·&nbsp;
    Proyecto Academico — Grupo 2
</div>
""", unsafe_allow_html=True)

with st.expander("Ver datos filtrados"):
    st.dataframe(dff.drop(columns=["Customer ID","Transaction ID"]), use_container_width=True, hide_index=True)
