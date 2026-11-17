def pregunta_12():
    """
    Para cada letra de la primera columna (`letter`), sume todos los valores
    numéricos de los pares `clave:valor` de la quinta columna (`metrics`).
    Retorne un diccionario `{letra: suma}` con las letras en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"A": 177, "B": 187, "C": 114, ...}
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

    resultado = (df.assign(metrics=df['metrics'].str.split(','))
                 .explode('metrics')
                 .assign(value=lambda data: data['metrics'].str.split(':').str[1].astype(int))
                 .groupby('letter')['value']
                 .sum()
                 .sort_index()
                 .to_dict())

    print(resultado)    

    return resultado

pregunta_12()
