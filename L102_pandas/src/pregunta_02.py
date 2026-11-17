def pregunta_02():
    """
    ¿Cuántas columnas tiene la tabla `data/tbl0.tsv`? Retorne la cantidad
    como un número entero.

    Ejemplo del formato de la respuesta:

        4
    """

    from pathlib import Path
    import pandas as pd

    ruta = Path(__file__).resolve().parents[1] / "data" / "tbl0.tsv"
    
    df = pd.read_csv(ruta, sep="\t")

    resultado = df.shape[1]
    print(resultado)

    return resultado

pregunta_02()
