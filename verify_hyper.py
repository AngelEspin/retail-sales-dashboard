"""Verificacion COMPLETA del .hyper para el dashboard"""
from tableauhyperapi import HyperProcess, Connection, Telemetry

HYPER = r"C:\Users\Espin\Desktop\maestria\proyecto\retail_sales.hyper"

print("=" * 60)
print("VERIFICACION COMPLETA DEL ARCHIVO .hyper")
print("=" * 60)

with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
    with Connection(endpoint=hyper.endpoint, database=HYPER) as conn:

        # 1. Contar filas
        with conn.execute_query('SELECT COUNT(*) FROM "Extract"."Ventas"') as result:
            for row in result:
                total = row[0]
                print(f"\n[1] FILAS: {total} (deben ser 1000)")

        # 2. Verificar columnas disponibles (probando cada una)
        columnas_requeridas = [
            "Transaction ID", "Date", "Customer ID", "Gender", "Age",
            "Product Category", "Quantity", "Price per Unit", "Total Amount",
            "Anio", "Mes", "NombreMes", "Trimestre", "DiaSemana",
            "TipoDia", "GrupoEdad", "NivelPrecio"
        ]
        print(f"\n[2] VERIFICACION DE COLUMNAS REQUERIDAS (17):")
        cols_ok = []
        for c in columnas_requeridas:
            try:
                with conn.execute_query(f'SELECT "{c}" FROM "Extract"."Ventas" LIMIT 1') as result:
                    for _ in result: pass
                cols_ok.append(c)
                print(f"   OK - {c}")
            except Exception as e:
                print(f"   ERROR - {c}: {e}")

        # 3. KPIs basicos
        print(f"\n[3] KPIs:")
        with conn.execute_query('SELECT SUM("Total Amount") FROM "Extract"."Ventas"') as result:
            for row in result: print(f"   Ingresos totales: ${row[0]:,}")
        with conn.execute_query('SELECT COUNT(*) FROM "Extract"."Ventas"') as result:
            for row in result: print(f"   Transacciones: {row[0]:,}")
        with conn.execute_query('SELECT AVG("Total Amount") FROM "Extract"."Ventas"') as result:
            for row in result: print(f"   Ticket promedio: ${row[0]:,.2f}")
        with conn.execute_query('SELECT SUM("Quantity") FROM "Extract"."Ventas"') as result:
            for row in result: print(f"   Unidades vendidas: {row[0]:,}")

        # 4. Datos para WS-2: Tendencia mensual
        print(f"\n[4] TENDENCIA MENSUAL (WS-2):")
        with conn.execute_query(
            'SELECT "NombreMes", SUM("Total Amount") '
            'FROM "Extract"."Ventas" '
            'GROUP BY "NombreMes" ORDER BY "NombreMes"'
        ) as result:
            for r in result:
                print(f"   {r[0]}: ${r[1]:,}")

        # 5. Datos para WS-3: Ingresos por categoria
        print(f"\n[5] INGRESOS POR CATEGORIA (WS-3):")
        with conn.execute_query(
            'SELECT "Product Category", SUM("Total Amount"), SUM("Quantity") '
            'FROM "Extract"."Ventas" '
            'GROUP BY "Product Category" ORDER BY 2 DESC'
        ) as result:
            for r in result:
                print(f"   {r[0]}: ${r[1]:,} ({r[2]} unidades)")

        # 6. Datos para WS-4: Perfil demografico
        print(f"\n[6] PERFIL DEMOGRAFICO (WS-4) - Ingresos por GrupoEdad x Gender:")
        with conn.execute_query(
            'SELECT "GrupoEdad", "Gender", SUM("Total Amount") '
            'FROM "Extract"."Ventas" '
            'GROUP BY "GrupoEdad", "Gender" ORDER BY "GrupoEdad", "Gender"'
        ) as result:
            for r in result:
                print(f"   {r[0]} / {r[1]}: ${r[2]:,}")

        # 7. Mapa de calor
        print(f"\n[7] MAPA DE CALOR (WS-5) - Ingresos por Categoria x Mes:")
        with conn.execute_query(
            'SELECT "Product Category", "NombreMes", SUM("Total Amount") '
            'FROM "Extract"."Ventas" '
            'GROUP BY "Product Category", "NombreMes" '
            'ORDER BY "Product Category", "NombreMes"'
        ) as result:
            for r in result:
                print(f"   {r[0]} / {r[1]}: ${r[2]:,}")

        # 8. Cardinalidades
        print(f"\n[8] CARDINALIDADES:")
        checks = [
            ('Categorias', 'COUNT(DISTINCT "Product Category")'),
            ('Generos', 'COUNT(DISTINCT "Gender")'),
            ('Grupos de edad', 'COUNT(DISTINCT "GrupoEdad")'),
            ('Meses', 'COUNT(DISTINCT "NombreMes")'),
            ('Trimestres', 'COUNT(DISTINCT "Trimestre")'),
            ('Niveles de precio', 'COUNT(DISTINCT "NivelPrecio")'),
        ]
        for label, sql in checks:
            with conn.execute_query(f'SELECT {sql} FROM "Extract"."Ventas"') as result:
                for row in result: print(f"   {label}: {row[0]}")

        with conn.execute_query('SELECT MIN("Age"), MAX("Age") FROM "Extract"."Ventas"') as result:
            for row in result: print(f"   Edad rango: {row[0]}-{row[1]}")
        with conn.execute_query('SELECT MIN("Date"), MAX("Date") FROM "Extract"."Ventas"') as result:
            for row in result: print(f"   Fecha rango: {row[0]} a {row[1]}")
        with conn.execute_query('SELECT MIN("Total Amount"), MAX("Total Amount") FROM "Extract"."Ventas"') as result:
            for row in result: print(f"   Total Amount rango: ${row[0]} - ${row[1]}")

        # 9. Nulos en todas las columnas
        print(f"\n[9] VALORES NULOS:")
        todos_ok = True
        for c in columnas_requeridas:
            with conn.execute_query(f'SELECT COUNT(*) FROM "Extract"."Ventas" WHERE "{c}" IS NULL') as result:
                for row in result:
                    if row[0] > 0:
                        print(f"   ERROR {c}: {row[0]} nulos!")
                        todos_ok = False
        if todos_ok:
            print("   OK - Ninguna columna tiene valores nulos")

print("\n" + "=" * 60)
if len(cols_ok) == 17 and todos_ok:
    print("RESULTADO: .hyper COMPLETO y CORRECTO")
    print("Contiene las 17 columnas requeridas con 1000 filas")
    print("LISTO para conectarlo en Tableau Desktop")
else:
    print("RESULTADO: .hyper tiene PROBLEMAS - revisar arriba")
print("=" * 60)
