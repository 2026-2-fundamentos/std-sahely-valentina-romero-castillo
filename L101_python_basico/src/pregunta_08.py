def pregunta_08():
    """
    Repita la pregunta 7, pero ahora cada lista de letras debe contener cada
    letra una sola vez y estar ordenada alfabéticamente. Retorne una lista de
    tuplas `(valor, letras)` ordenada por el valor.

    Ejemplo del formato de la respuesta:

        [(0, ["C"]), (1, ["B", "E"]), (2, ["A", "E"]), ...]
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

    resultado = df.groupby("value")["letter"].apply(lambda x: sorted(list(set(x)))).reset_index().sort_values("value").apply(tuple, axis=1).tolist()
    
    return resultado

pregunta_08()