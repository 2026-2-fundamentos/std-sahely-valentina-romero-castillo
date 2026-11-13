def pregunta_01():
    """
    Calcule la suma de los valores de la segunda columna (`value`) del
    archivo `data/data.csv.gz` y retorne el resultado como un número entero.

    Ejemplo del formato de la respuesta:

        214
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

    return int(df['value'].sum())


pregunta_01()