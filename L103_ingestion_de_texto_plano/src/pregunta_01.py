def pregunta_01():
    """
    El archivo `data/clusters_report.txt` es un reporte de clústeres de
    palabras clave pensado para ser leído por una persona, no por un programa:
    los encabezados ocupan varias líneas, las columnas están alineadas con
    espacios y la lista de palabras clave de un clúster continúa en las líneas
    siguientes.

    Su tarea es convertir ese reporte en un DataFrame de Pandas con una fila
    por clúster y las columnas:

    - `cluster`: número del clúster, como entero.
    - `cantidad_de_palabras_clave`: como entero.
    - `porcentaje_de_palabras_clave`: como número decimal; por ejemplo, el
      texto `15,9 %` debe quedar como `15.9`.
    - `principales_palabras_clave`: todas las palabras clave del clúster en un
      solo texto, separadas por una coma y un único espacio.

    Retorne el DataFrame.

    Ejemplo del formato de la respuesta (se omite la última columna):

           cluster  cantidad_de_palabras_clave  porcentaje_de_palabras_clave
        0        1                         105                          15.9
        1        2                         102                          15.4
        ...
    """

    from pathlib import Path
    import pandas as pd
    import re

    ruta = Path(__file__).resolve().parents[1] / "data" / "clusters_report.txt"

    registros = []
    registro_actual = None

    with ruta.open(encoding="utf-8") as archivo:
        
        for linea in archivo:
            coincidencia = re.match(r"^\s*(\d+)\s+(\d+)\s+([\d,]+)\s+%\s+(.*)$",linea.rstrip())

            if coincidencia:
                if registro_actual is not None:
                    registros.append(registro_actual)

                cluster, cantidad, porcentaje, palabras = coincidencia.groups()
                registro_actual = [int(cluster), int(cantidad), float(porcentaje.replace(",", ".")), palabras]

            elif registro_actual is not None and linea.strip():
                registro_actual[3] += " " + linea.strip()

    if registro_actual is not None:
        registros.append(registro_actual)

    df = pd.DataFrame(registros,columns=["cluster","cantidad_de_palabras_clave","porcentaje_de_palabras_clave","principales_palabras_clave",])

    df["principales_palabras_clave"] = (df["principales_palabras_clave"].str.replace(r"\s+", " ", regex=True).str.replace(r"\s*,\s*", ", ", regex=True).str.rstrip("., "))

    print(df.head())

    return df

pregunta_01()
