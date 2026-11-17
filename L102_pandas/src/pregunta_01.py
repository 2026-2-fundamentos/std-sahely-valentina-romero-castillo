def pregunta_01():
    """
    ¿Cuántos registros tiene la tabla `data/tbl0.tsv`? Retorne la cantidad
    como un número entero.

    Ejemplo del formato de la respuesta:

        40
    """

    from pathlib import Path
    import pandas as pd

    ruta = Path(__file__).resolve().parents[1] / "data" / "tbl0.tsv"
    
    df = pd.read_csv(ruta, sep="\t")

    resultado = df.shape[0]
    print(resultado)

    return resultado

pregunta_01()
    

