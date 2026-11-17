def pregunta_06():
    """
    La quinta columna (`metrics`) contiene pares `clave:valor` separados por
    comas. Para cada clave, encuentre el valor mínimo y el valor máximo que
    aparecen en todo el archivo. Retorne una lista de tuplas
    `(clave, mínimo, máximo)` ordenada alfabéticamente por la clave.

    Observe que el orden es mínimo y luego máximo, al contrario de la
    pregunta 5.

    Ejemplo del formato de la respuesta:

        [("aaa", 1, 9), ("bbb", 1, 9), ...]
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

    metricas = (
        df["metrics"]
        .str.split(",", expand=True)
        .stack()
        .str.split(":", expand=True)
    )
    metricas[1] = metricas[1].astype(int)

    resultado = (
        metricas.groupby(0)[1]
        .agg(min="min", max="max")
        .reset_index()
        .sort_values(0)
        .apply(tuple, axis=1)
        .tolist()
    )

    print(resultado)

    return resultado

pregunta_06()