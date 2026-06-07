"""
Genera un archivo .twb optimizado para Tableau Public.
El formato sigue la estructura XML que Tableau espera.
"""
import xml.etree.ElementTree as ET
import xml.dom.minidom
import os

BASE = r"C:\Users\Espin\Desktop\maestria\proyecto"
CSV_FILENAME = "retail_sales_clean.csv"
TWB_PATH = os.path.join(BASE, "retail_sales_dashboard.twb")

def esc(text):
    """XML-escape text"""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

wb = ET.Element("workbook")

# Basic workbook attributes
wb.set("source", "local")
wb.set("version", "2024.2")

# ==============================
# DATASOURCE
# ==============================
ds = ET.SubElement(wb, "datasource")
ds.set("caption", "retail_sales_clean")
ds.set("name", "retail_sales_clean")
ds.set("inline", "true")
ds.set("version", "2024.2")

# Connection to CSV
conn = ET.SubElement(ds, "connection")
conn.set("class", "csv")
conn.set("dbname", "[" + CSV_FILENAME + "]")

# Named connection
ncs = ET.SubElement(conn, "named-connections")
ET.SubElement(ncs, "named-connection", {"name": "csv-connection"})

# Relation
rel = ET.SubElement(conn, "relation")
rel.set("type", "table")
rel.set("name", CSV_FILENAME.replace(".csv", ""))
rel.set("table", "[" + CSV_FILENAME.replace(".csv", "") + "$]")

# Columns
cols_elem = ET.SubElement(conn, "cols")

all_cols = [
    ("Transaction ID", "integer", "dimension"),
    ("Date", "date", "dimension"),
    ("Customer ID", "string", "dimension"),
    ("Gender", "string", "dimension"),
    ("Age", "integer", "measure"),
    ("Product Category", "string", "dimension"),
    ("Quantity", "integer", "measure"),
    ("Price per Unit", "integer", "measure"),
    ("Total Amount", "integer", "measure"),
    ("Anio", "integer", "dimension"),
    ("Mes", "integer", "dimension"),
    ("NombreMes", "string", "dimension"),
    ("Trimestre", "string", "dimension"),
    ("DiaSemana", "string", "dimension"),
    ("TipoDia", "string", "dimension"),
    ("GrupoEdad", "string", "dimension"),
    ("NivelPrecio", "string", "dimension"),
]

for name, dtype, role in all_cols:
    col = ET.SubElement(cols_elem, "col")
    col.set("name", "[" + name + "]")
    col.set("type", dtype)
    col.set("role", role)

# Layout dimensions
layout = ET.SubElement(ds, "layout-dimensions")

# Folder: Originales
f_orig = ET.SubElement(layout, "folder", {"name": "Originales"})
for name, dtype, role in all_cols[:9]:
    dim = ET.SubElement(f_orig, "dimension")
    dim.set("key", "[TableauDatabase].[" + name + "]")
    dim.set("name", name)
    dim.set("type", dtype)
    dim.set("datatype", dtype)

# Folder: Derivados
f_deriv = ET.SubElement(layout, "folder", {"name": "Derivados"})
for name, dtype, role in all_cols[9:]:
    dim = ET.SubElement(f_deriv, "dimension")
    dim.set("key", "[TableauDatabase].[" + name + "]")
    dim.set("name", name)
    dim.set("type", dtype)
    dim.set("datatype", dtype)

ET.SubElement(ds, "aliases")
ET.SubElement(ds, "semantic-values")

# ==============================
# WORKSHEETS
# ==============================
# Helper to add a worksheet
def add_ws(name, title, mark_class, columns_xml, rows_xml, encodings_list):
    ws = ET.SubElement(wb, "worksheet", {"name": name})
    # Title
    ttl = ET.SubElement(ws, "title")
    ttl.text = title
    # Table/view
    tbl = ET.SubElement(ws, "table")
    view = ET.SubElement(tbl, "view")
    # Columns
    cols_el = ET.SubElement(view, "columns")
    for c in columns_xml:
        cols_el.append(c)
    # Rows
    rows_el = ET.SubElement(view, "rows")
    for r in rows_xml:
        rows_el.append(r)
    # Filter (empty)
    ET.SubElement(view, "filter")
    # Marks
    marks = ET.SubElement(view, "marks")
    mark = ET.SubElement(marks, "mark", {"class": mark_class})
    encs = ET.SubElement(mark, "encodings")
    for enc_attrs in encodings_list:
        ET.SubElement(encs, "encoding", enc_attrs)

def col_f(field, dtype="string", role="dimension"):
    el = ET.Element("column")
    el.set("field", field)
    el.set("datatype", dtype)
    el.set("role", role)
    return el

def row_f(field, dtype="string", role="dimension"):
    el = ET.Element("row")
    el.set("field", field)
    el.set("datatype", dtype)
    el.set("role", role)
    return el

# WS-1: KPIs (4 separate sheets)
add_ws("WS-1A KPI Ingresos", "Ingresos totales", "Text",
       [], [],
       [{"class": "text", "field": "SUM([Total Amount])", "aggregation": "SUM", "datatype": "integer", "role": "measure"}])

add_ws("WS-1B KPI Transacciones", "Transacciones", "Text",
       [], [],
       [{"class": "text", "field": "COUNT([Transaction ID])", "aggregation": "COUNT", "datatype": "integer", "role": "measure"}])

add_ws("WS-1C KPI Ticket Promedio", "Ticket promedio", "Text",
       [], [],
       [{"class": "text", "field": "SUM([Total Amount])/COUNT([Transaction ID])", "aggregation": "SUM", "datatype": "integer", "role": "measure"}])

add_ws("WS-1D KPI Unidades", "Unidades vendidas", "Text",
       [], [],
       [{"class": "text", "field": "SUM([Quantity])", "aggregation": "SUM", "datatype": "integer", "role": "measure"}])

# WS-2: Tendencia mensual (line chart)
add_ws("WS-2 Tendencia Mensual", "Ingresos por mes (2023)", "Line",
       [col_f("[NombreMes]", "string", "dimension")],
       [row_f("SUM([Total Amount])", "integer", "measure")],
       [{"class": "color", "field": "[Product Category]", "datatype": "string", "role": "dimension"}])

# WS-3: Ingresos por categoria (horizontal bar)
add_ws("WS-3 Ingresos por Categoria", "Ingresos por Categoria", "Bar",
       [col_f("SUM([Total Amount])", "integer", "measure")],
       [row_f("[Product Category]", "string", "dimension")],
       [
           {"class": "color", "field": "[Product Category]", "datatype": "string", "role": "dimension"},
           {"class": "label", "field": "SUM([Total Amount])", "aggregation": "SUM", "datatype": "integer", "role": "measure"},
       ])

# WS-4: Perfil demografico (grouped bar)
add_ws("WS-4 Perfil Demografico", "Ingresos por Grupo de Edad y Genero", "Bar",
       [
           col_f("[GrupoEdad]", "string", "dimension"),
           col_f("[Gender]", "string", "dimension"),
       ],
       [row_f("SUM([Total Amount])", "integer", "measure")],
       [{"class": "color", "field": "[Gender]", "datatype": "string", "role": "dimension"}])

# WS-5: Mapa de calor (highlight table)
add_ws("WS-5 Mapa de Calor Cat x Mes", "Mapa de Calor - Ingresos por Categoria y Mes", "Square",
       [col_f("[NombreMes]", "string", "dimension")],
       [row_f("[Product Category]", "string", "dimension")],
       [
           {"class": "color", "field": "SUM([Total Amount])", "aggregation": "SUM", "datatype": "integer", "role": "measure"},
           {"class": "label", "field": "SUM([Total Amount])", "aggregation": "SUM", "datatype": "integer", "role": "measure"},
       ])

# ==============================
# DASHBOARD
# ==============================
db = ET.SubElement(wb, "dashboard")
db.set("name", "Dashboard - Ventas Minoristas 2023")

# Dashboard size
size = ET.SubElement(db, "size")
size.set("max", "-1")
size.set("min", "-1")
size.set("screen", "desktop")

# Layout (basic structure)
layout = ET.SubElement(db, "layout")

# We'll add a simple layout with items
# Row 0: Title text
dash_title = ET.SubElement(layout, "dashboard-item", {"name": "Análisis Visual de Ventas Minoristas 2023"})
ET.SubElement(dash_title, "zone", {"type": "text"})

# Row 1: 4 KPIs in horizontal zone
kpi_zone = ET.SubElement(layout, "dashboard-item", {"name": "row-kpis"})
kpi_hzon = ET.SubElement(kpi_zone, "zone", {"type": "hzon"})
for name in ["WS-1A KPI Ingresos", "WS-1B KPI Transacciones", "WS-1C KPI Ticket Promedio", "WS-1D KPI Unidades"]:
    item = ET.SubElement(kpi_zone, "dashboard-item", {"name": name})
    ET.SubElement(item, "zone", {"type": "view"})

# Row 2: Trend + Category
row2 = ET.SubElement(layout, "dashboard-item", {"name": "row-main"})
ET.SubElement(row2, "zone", {"type": "hzon"})
for name in ["WS-2 Tendencia Mensual", "WS-3 Ingresos por Categoria"]:
    item = ET.SubElement(row2, "dashboard-item", {"name": name})
    ET.SubElement(item, "zone", {"type": "view"})

# Row 3: Demographics + Heatmap
row3 = ET.SubElement(layout, "dashboard-item", {"name": "row-bottom"})
ET.SubElement(row3, "zone", {"type": "hzon"})
for name in ["WS-4 Perfil Demografico", "WS-5 Mapa de Calor Cat x Mes"]:
    item = ET.SubElement(row3, "dashboard-item", {"name": name})
    ET.SubElement(item, "zone", {"type": "view"})

# Filter actions placeholder
ET.SubElement(db, "filter-actions")

# Group info text item
grp_item = ET.SubElement(layout, "dashboard-item", {"name": "Grupo 2 - Angel Espin & Carlos Ramirez"})
ET.SubElement(grp_item, "zone", {"type": "text"})

# ==============================
# WINDOWS
# ==============================
ET.SubElement(wb, "windows")

# ==============================
# WRITE FILE
# ==============================
xml_str = ET.tostring(wb, encoding="unicode")
dom = xml.dom.minidom.parseString(xml_str)
pretty = dom.toprettyxml(indent="  ")

with open(TWB_PATH, "w", encoding="utf-8") as f:
    f.write(pretty)

print("TWB generado:", TWB_PATH)
print("Tamanio:", os.path.getsize(TWB_PATH), "bytes")
print()
print("Worksheets incluidos:")
for ws_name in ["WS-1A KPI Ingresos", "WS-1B KPI Transacciones", "WS-1C KPI Ticket Promedio", "WS-1D KPI Unidades",
                "WS-2 Tendencia Mensual", "WS-3 Ingresos por Categoria",
                "WS-4 Perfil Demografico", "WS-5 Mapa de Calor Cat x Mes"]:
    print(f"  - {ws_name}")
print()
print("Dashboard: Dashboard - Ventas Minoristas 2023")
