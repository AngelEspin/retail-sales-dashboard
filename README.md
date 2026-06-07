# Dashboard de Ventas Minoristas 2023 — Grupo 2

**Integrantes:** Angel Espin · Carlos Ramirez

Dashboard interactivo de ventas minoristas construido con Streamlit,
replicando el dashboard original de Tableau.

## Dataset

- **Fuente:** [Retail Sales Dataset (Kaggle)](https://www.kaggle.com/datasets/mohammadtalib786/retail-sales-dataset)
- **Archivo:** `retail_sales_clean.csv` (limpio, con atributos derivados)

## Visualizaciones incluidas

1. **KPIs** — Ingresos totales, transacciones, ticket promedio, unidades
2. **Tendencia mensual** — Linea de ingresos por mes (con desglose por categoria)
3. **Ingresos por categoria** — Barras horizontales ordenadas
4. **Perfil demografico** — Barras agrupadas: edad x genero
5. **Mapa de calor** — Categoria x Mes (highlight table)
6. **Filtros interactivos** — Trimestre, genero, categoria

## Como desplegar en Streamlit Cloud

### Opcion 1: Directo desde GitHub (recomendada)

1. Sube estos archivos a un repositorio de GitHub:
   - `streamlit_app.py`
   - `requirements.txt`
   - `retail_sales_clean.csv`
   - `README.md` (este archivo)

2. Ve a https://streamlit.io/cloud

3. Inicia sesion con tu cuenta de GitHub

4. Haz clic en **"New app"**

5. Selecciona:
   - Repositorio: `tu-usuario/tu-repo`
   - Branch: `main`
   - Main file path: `streamlit_app.py`

6. Haz clic en **"Deploy"**

7. En ~2 minutos tendras tu dashboard publico en linea

### Opcion 2: Local (para prueba)

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Requisitos

- Python 3.9+
- streamlit
- pandas
- numpy
- plotly

## Estructura del proyecto

```
proyecto/
  streamlit_app.py       # App de Streamlit
  requirements.txt       # Dependencias
  retail_sales_clean.csv # Datos limpios (17 columnas, 1000 filas)
  README.md              # Esta documentacion
```

## Notas

- Los datos son sinteticos (Kaggle) — 1000 transacciones del ano 2023
- Todos los atributos derivados (NombreMes, Trimestre, GrupoEdad, NivelPrecio, etc.)
  ya estan precalculados en el CSV
- La app replica exactamente las 5 vistas del dashboard original de Tableau
