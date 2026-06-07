# Dashboard de Ventas Minoristas 2023 — Grupo 2

**Integrantes:** Angel Espin · Carlos Ramirez

Dashboard interactivo para explorar ventas minoristas desde tres angulos:
tiempo, producto y cliente. Construido con **Streamlit** + **Plotly**.

---

## Dataset

**Fuente:** [Retail Sales Dataset (Kaggle)](https://www.kaggle.com/datasets/mohammadtalib786/retail-sales-dataset)

**Descripcion:** 1,000 transacciones sinteticas de una tienda minorista durante el ano 2023.
Cada fila representa una compra con 9 atributos originales.

**Atributos originales:**

| Atributo | Tipo | Descripcion |
|---|---|---|
| Transaction ID | Categorico (clave) | Identificador unico de la compra |
| Date | Temporal | Fecha de la transaccion |
| Customer ID | Categorico (clave) | Identificador del cliente |
| Gender | Categorico | Genero del cliente (Female / Male) |
| Age | Cuantitativo | Edad del cliente (18-64) |
| Product Category | Categorico | Categoria del producto (Beauty, Clothing, Electronics) |
| Quantity | Cuantitativo discreto | Unidades compradas (1-4) |
| Price per Unit | Cuantitativo | Precio unitario ($25, $30, $50, $300, $500) |
| Total Amount | Cuantitativo | Importe total (= Quantity x Price per Unit) |

## Preprocesamiento (ver preprocessing.ipynb)

El cuaderno `preprocessing.ipynb` documenta el proceso completo:

### 1. Validacion de calidad
- **0 valores nulos** en las 9 columnas originales
- **0 filas duplicadas**
- **Consistencia aritmetica:** Total Amount = Quantity x Price per Unit en 100% de los casos
- Rango temporal: 2023-01-01 a 2024-01-01 (998 transacciones en 2023, 2 en 2024)

### 2. Derivacion de atributos (8 nuevos)

| Atributo derivado | Derivado de | Descripcion |
|---|---|---|
| Anio | Date | Ano de la transaccion |
| Mes | Date | Mes numerico (1-12) |
| NombreMes | Date | Mes con formato "01-Enero", "02-Febrero", ... |
| Trimestre | Date | Trimestre (T1, T2, T3, T4) |
| DiaSemana | Date | Dia de la semana con formato "1-Lunes", ... |
| TipoDia | Date | "Entre semana" o "Fin de semana" |
| GrupoEdad | Age | Bins etarios: 18-25, 26-35, 36-45, 46-55, 56-65 |
| NivelPrecio | Price per Unit | "Bajo (<=50)" o "Alto (>=300)" |

### 3. Dataset final
- **1,000 filas** x **17 columnas** (9 originales + 8 derivadas)
- Exportado como `retail_sales_clean.csv` (codificado UTF-8)

---

## Visualizaciones

El dashboard incluye **5 vistas** que responden a **3 tareas abstractas**:

### Tarea 1 — Descubrir tendencias en el tiempo
- **WS-1:** KPIs (ingresos totales, transacciones, ticket promedio, unidades)
- **WS-2:** Tendencia mensual de ingresos (grafico de lineas)

### Tarea 2 — Comparar y ordenar entre categorias
- **WS-3:** Ingresos y unidades por categoria (barras horizontales ordenadas)
- **WS-5:** Mapa de calor Categoria x Mes (highlight table)

### Tarea 3 — Caracterizar la distribucion demografica
- **WS-4:** Perfil demografico: ingresos por grupo de edad y genero (barras agrupadas)

### Filtros interactivos (sidebar)
- Por **Trimestre** (T1, T2, T3, T4)
- Por **Genero** (Female, Male)
- Por **Categoria** (Beauty, Clothing, Electronics)

---

## Como ejecutar localmente

```bash
# 1. Clonar o descargar esta carpeta
# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la app
streamlit run streamlit_app.py
```

## Como desplegar en Streamlit Cloud

1. Sube **todos los archivos de esta carpeta** a un repositorio de GitHub:

```
dashboard_streamlit/
  streamlit_app.py         # App principal
  retail_sales_clean.csv    # Datos limpios (17 col, 1000 filas)
  preprocessing.ipynb       # Cuaderno de limpieza y derivacion
  requirements.txt          # Dependencias
  README.md                 # Esta documentacion
```

2. Ve a [Streamlit Cloud](https://streamlit.io/cloud) e inicia sesion con GitHub

3. Haz clic en **"New app"** y configura:
   - **Repository:** `tu-usuario/tu-repo`
   - **Branch:** `main`
   - **Main file path:** `dashboard_streamlit/streamlit_app.py`

4. Haz clic en **"Deploy"**

5. En aproximadamente **2 minutos** tendras el dashboard en linea con una URL publica.

---

## Tecnologias usadas

- **Python** 3.9+ — preprocesamiento
- **Pandas** — manipulacion de datos
- **Plotly** — graficos interactivos
- **Streamlit** — framework de dashboard
- **Dataset:** [Retail Sales Dataset](https://www.kaggle.com/datasets/mohammadtalib786/retail-sales-dataset) (Kaggle)

---

*Proyecto Academico — Analisis Visual de Ventas Minoristas 2023*
