def pregunta_01():
    """
    El archivo `data/solicitudes_de_credito.csv.gz` contiene las solicitudes de
    un programa de crédito, pero llegó sucio: tiene una columna de índice que
    no pertenece a los datos, registros duplicados, registros incompletos y
    valores que representan lo mismo escritos de formas distintas en los
    campos de texto, las fechas, el estrato y el monto.

    Su tarea es limpiarlo y guardar el resultado en
    `submission/solicitudes_de_credito.csv`, usando punto y coma (`;`) como
    separador y sin el índice de Pandas.

    El archivo limpio debe cumplir lo siguiente:

    - Contiene solamente las nueve columnas `sexo`, `tipo_de_emprendimiento`,
      `idea_negocio`, `barrio`, `estrato`, `comuna_ciudadano`,
      `fecha_de_beneficio`, `monto_del_credito` y `línea_credito`, en ese
      orden.
    - Los campos de texto están en minúsculas y sus palabras separadas por
      espacios.
    - `estrato` y `monto_del_credito` son números enteros, sin símbolos ni
      separadores de miles.
    - Todas las fechas de `fecha_de_beneficio` usan un mismo formato, por
      ejemplo `AAAA-MM-DD`.
    - No hay registros incompletos. La única excepción es
      `comuna_ciudadano`: sus valores faltantes son parte de los datos
      originales y deben conservarse.
    - No hay registros duplicados.

    Ejemplo del formato del archivo:

        sexo;tipo_de_emprendimiento;idea_negocio;barrio;estrato;...
        femenino;comercio;almacen de ropa en;los cerros el vergel;2;...
        ...
    """

    import re
    from pathlib import Path

    import pandas as pd

    activity_dir = Path(__file__).resolve().parents[1]
    data_path = activity_dir / "data" / "solicitudes_de_credito.csv.gz"

    df = pd.read_csv(data_path, sep=";", encoding="utf-8")

    df = df.drop(columns=["Unnamed: 0"])

    def normalize_header(header):
        normalized = str(header).lower().strip()
        normalized = normalized.lstrip("\ufeff")
        return re.sub(r"\s+", "_", normalized)

    df.columns = [normalize_header(column) for column in df.columns]
    df = df.rename(
        columns={
            column: "línea_credito"
            for column in df.columns
            if "nea_credito" in column
        }
    )

    text_columns = [
        "sexo",
        "tipo_de_emprendimiento",
        "idea_negocio",
        "barrio",
        "línea_credito",
    ]

    for column in text_columns:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
            .str.lower()
            .str.replace(r"[_-]+", " ", regex=True)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

    df["estrato"] = pd.to_numeric(df["estrato"], errors="coerce").astype("Int64")

    date_values = df["fecha_de_beneficio"].astype("string").str.strip()
    df["fecha_de_beneficio"] = pd.to_datetime(
        date_values,
        format="mixed",
        dayfirst=True,
        errors="coerce",
    ).dt.strftime("%Y-%m-%d")

    monto_limpio = (
        df["monto_del_credito"]
        .astype("string")
        .str.strip()
        .str.replace(r"[$,]", "", regex=True)
    )
    df["monto_del_credito"] = pd.to_numeric(
        monto_limpio,
        errors="coerce",
    ).round().astype("Int64")

    expected_columns = [
        "sexo",
        "tipo_de_emprendimiento",
        "idea_negocio",
        "barrio",
        "estrato",
        "comuna_ciudadano",
        "fecha_de_beneficio",
        "monto_del_credito",
        "línea_credito",
    ]
    df = df[expected_columns]

    df = df.dropna(subset=[column for column in expected_columns if column != "comuna_ciudadano"])
    df = df.drop_duplicates()

    submission_dir = activity_dir / "submission"
    submission_dir.mkdir(parents=True, exist_ok=True)
    output_path = submission_dir / "solicitudes_de_credito.csv"
    df.to_csv(output_path, sep=";", index=False, encoding="utf-8")