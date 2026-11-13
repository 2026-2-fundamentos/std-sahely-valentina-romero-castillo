def pregunta_02():
    """
    Cuente cuántos registros hay para cada letra de la primera columna
    (`letter`). Retorne una lista de tuplas `(letra, cantidad)` ordenada
    alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 8), ("B", 7), ("C", 5), ...]
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

    resultado = df.groupby('letter').size().reset_index(name='count').sort_values('letter').apply(tuple, axis=1).tolist()
    print(resultado)

    return resultado

pregunta_02()

