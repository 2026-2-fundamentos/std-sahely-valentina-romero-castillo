def main():
    """
    Antes de limpiar o analizar un conjunto de datos, un analista debe
    documentar qué problemas tiene. En este laboratorio usted no va a limpiar
    `data/ventas.csv.gz`: va a construir un reporte de calidad que deje evidencia
    de sus problemas, tal como están en el archivo.

    Lea `data/ventas.csv.gz` sin modificar sus valores. Para trabajar con los
    encabezados, normalícelos: páselos a minúsculas, elimine los espacios al
    inicio y al final (y cualquier marca BOM) y reemplace los espacios
    internos por `_`. Las columnas requeridas son `supplier_id`, `supplier`,
    `country`, `city`, `purchase_date`, `amount`, `discount`, `weight`,
    `units`, `unit_price` y `contact_email`.

    Escriba el reporte en `submission/data_quality_report.json` con estas
    claves:

    - `row_count`: cantidad de filas de datos.
    - `column_count`: cantidad de columnas.
    - `missing_required_columns`: lista ordenada de columnas requeridas que no
      están en el archivo.
    - `unexpected_columns`: lista ordenada de columnas del archivo que no son
      requeridas.
    - `duplicate_row_count`: cantidad de filas idénticas a una fila anterior.
    - `duplicate_supplier_id_row_count`: cantidad de filas cuyo `supplier_id`
      aparece más de una vez (cuente todas esas filas, no solo las
      repetidas).
    - `missing_value_count_by_column`: diccionario con la cantidad de valores
      faltantes de cada columna. Considere faltantes las celdas vacías y las
      que contienen `N/A`.
    - `invalid_email_count`: cantidad de valores de `contact_email` que no
      tienen la forma `usuario@dominio.extension`.
    - `invalid_unit_count`: cantidad de valores numéricos de `units` que no son
      enteros positivos. Los valores faltantes no se cuentan aquí.
    - `country_values`: lista ordenada de los valores distintos de `country`,
      escritos exactamente como aparecen en el archivo.

    La función también debe retornar el reporte como un diccionario.

    Ejemplo del formato del reporte:

        {
          "row_count": 103,
          "column_count": 11,
          "missing_required_columns": [],
          ...
          "country_values": [" Colombia ", "CO", ...]
        }
    """

    # Librerías necesarias

    import json
    import re
    from pathlib import Path
    import pandas as pd

    # Definición de rutas

    activity_dir = Path(__file__).resolve().parents[1]
    data_path = activity_dir / "data" / "ventas.csv.gz"
    submission_dir = activity_dir / "submission"

    # Lectura del archivo CSV
    df = pd.read_csv(data_path)

    # Función para normalizar los nombres de las columnas

    def normalize_column(column):
        normalized = str(column).lower().strip()
        normalized = normalized.lstrip("\ufeff")
        return re.sub(r"\s+", "_", normalized)

    df.columns = [normalize_column(column) for column in df.columns]

    required_columns = [
        "supplier_id",
        "supplier",
        "country",
        "city",
        "purchase_date",
        "amount",
        "discount",
        "weight",
        "units",
        "unit_price",
        "contact_email",
    ]

    # Validación de datos

    missing_required_columns = [
        column for column in required_columns if column not in df.columns
    ]

    # Validación de columnas inesperadas
    
    unexpected_columns = sorted(
        column for column in df.columns if column not in required_columns
    )

    duplicate_row_count = int(df.duplicated().sum())

    if "supplier_id" in df.columns:
        supplier_id_counts = df["supplier_id"].value_counts(dropna=False)
        duplicate_supplier_id_row_count = int(
            supplier_id_counts[supplier_id_counts > 1].sum()
        )
    else:
        duplicate_supplier_id_row_count = 0

    missing_value_count_by_column = {}
    for column in df.columns:
        missing_values = df[column].isna()
        if df[column].dtype == "object":
            missing_values |= df[column].astype(str).str.strip().isin(
                ["", "N/A"]
            )
        missing_value_count_by_column[column] = int(missing_values.sum())

    if "contact_email" in df.columns:
        email_pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
        email_values = df["contact_email"].dropna()
        invalid_email_count = int(
            (~email_values.astype(str).str.strip().str.match(email_pattern)).sum()
        )
    else:
        invalid_email_count = 0

    if "units" in df.columns:
        unit_values = df["units"].dropna()
        numeric_units = pd.to_numeric(unit_values, errors="coerce")
        invalid_unit_count = int(
            (
                numeric_units.notna()
                & (
                    (numeric_units <= 0)
                    | (numeric_units % 1 != 0)
                )
            ).sum()
        )
    else:
        invalid_unit_count = 0

    if "country" in df.columns:
        country_values = sorted(
            df["country"].dropna().astype(str).unique(),
            key=lambda value: value,
        )
    else:
        country_values = []

    report = {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "missing_required_columns": missing_required_columns,
        "unexpected_columns": unexpected_columns,
        "duplicate_row_count": duplicate_row_count,
        "duplicate_supplier_id_row_count": duplicate_supplier_id_row_count,
        "missing_value_count_by_column": missing_value_count_by_column,
        "invalid_email_count": invalid_email_count,
        "invalid_unit_count": invalid_unit_count,
        "country_values": country_values,
    }

    report_path = submission_dir / "data_quality_report.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=4),
        encoding="utf-8",
    )

    return report
