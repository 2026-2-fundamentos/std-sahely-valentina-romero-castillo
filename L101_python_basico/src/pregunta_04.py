def pregunta_04():
    """
    Cuente cuántos registros hay en cada mes, usando la fecha de la tercera
    columna (`date`). Represente el mes como un texto de dos dígitos y retorne
    una lista de tuplas `(mes, cantidad)` ordenada por el mes.

    Ejemplo del formato de la respuesta:

        [("01", 3), ("02", 4), ("03", 2), ...]
    """

    from pathlib import Path
    import pandas as pd
    
    ruta = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"
        
    df = pd.read_csv(
        ruta,
        sep="\t",
        header=None,
        names=["letter", "value", "date", "codes", "metrics"],
        compression="gzip",
    )

    df.loc[df["date"] == "1999-02-29", "date"] = "1999-02-28"

    df["date"] = pd.to_datetime(df["date"],format="%Y-%m-%d", errors="coerce")

    resultado = list(df.dropna(subset=["date"]).groupby(df["date"].dt.strftime("%m")).size() .sort_index().items())

    return resultado


pregunta_04()