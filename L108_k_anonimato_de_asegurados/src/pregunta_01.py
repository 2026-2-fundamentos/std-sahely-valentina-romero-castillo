def pregunta_01():
    """
    Una aseguradora quiere publicar datos de sus afiliados para que un grupo
    de investigación estudie el costo de los seguros, sin que nadie pueda
    reconocer a una persona. El archivo `data/insurance.csv.gz` tiene una fila
    por afiliado con su edad (`age`), sexo (`sex`), índice de masa corporal
    (`bmi`), número de hijos (`children`), si fuma (`smoker`), región
    (`region`) y el costo de su seguro (`charges`).

    El archivo no tiene nombres ni documentos, pero eso no basta: la edad, el
    sexo, el índice de masa corporal, el número de hijos y la región son
    cuasi-identificadores, porque combinados pueden señalar a una persona.
    `smoker` es el atributo sensible que se quiere proteger.

    En este laboratorio usted va a medir el riesgo de reidentificación y a
    decidir qué publicar. Use estas definiciones:

    - Una clase de equivalencia es un grupo de registros con los mismos
      valores en todos los cuasi-identificadores. Un conjunto de datos cumple
      k-anonimato si toda clase tiene al menos k registros. Use k = 5.
    - `age_group`: `18-29`, `30-39`, `40-49` o `50-64`.
    - `bmi_group`: `bajo peso` (menos de 18.5), `normal` (desde 18.5 y menos
      de 25), `sobrepeso` (desde 25 y menos de 30) u `obesidad` (30 o más).
    - `children_group`: `0`, `1-2` o `3+`.

    Evalúe dos esquemas de generalización:

    - `with_children`: `age_group`, `sex`, `bmi_group`, `children_group` y
      `region`.
    - `without_children`: `age_group`, `sex`, `bmi_group` y `region`; el
      número de hijos no se publica.

    En cada esquema, suprima (no publique) los registros de las clases con
    menos de 5 registros. Luego, entre las clases publicadas, identifique las
    que no tienen diversidad en el atributo sensible, es decir, aquellas en
    las que todos los afiliados fuman o ninguno fuma: en esas clases, saber
    que alguien pertenece a ellas revela si fuma.

    Escriba `submission/privacy_report.json` con estas claves:

    - `original_k`: el menor tamaño de clase usando los cuasi-identificadores
      originales, sin generalizar.
    - `original_unique_records`: cuántos registros son los únicos de su clase
      con los cuasi-identificadores originales.
    - `schemes`: un diccionario con una entrada por esquema (`with_children` y
      `without_children`), cada una con las claves `quasi_identifiers` (la
      lista de columnas del esquema), `equivalence_classes` (clases antes de
      suprimir), `k_before_suppression`, `suppressed_records`,
      `published_records`, `published_classes`,
      `classes_without_smoker_diversity` y
      `records_without_smoker_diversity`.
    - `selected_scheme`: el esquema que suprime menos registros.
    - `mean_charges_original` y `mean_charges_published`: el costo promedio
      de todos los afiliados y el de los registros publicados con el esquema
      seleccionado.
    - `smoker_rate_original` y `smoker_rate_published`: la proporción de
      fumadores en ambos casos.

    Escriba también `submission/insurance_published.csv`, sin el índice de
    Pandas, con los registros publicados del esquema seleccionado, en el
    mismo orden del archivo original, y las columnas del esquema seguidas de
    `smoker` y `charges`.

    La función también debe retornar el reporte como un diccionario.

    Ejemplo del formato del reporte:

        {
          "original_k": 1,
          "original_unique_records": 1330,
          "schemes": {
            "with_children": {
              "quasi_identifiers": ["age_group", "sex", ...],
              "equivalence_classes": 278,
              ...
            },
            ...
          },
          ...
        }
    """

    import json
    from pathlib import Path

    import pandas as pd

    activity_dir = Path(__file__).resolve().parents[1]
    data_path = activity_dir / "data" / "insurance.csv.gz"
    submission_dir = activity_dir / "submission"
    submission_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(data_path)
    k = 5

    df["age_group"] = pd.cut(
        df["age"],
        bins=[18, 30, 40, 50, 65],
        right=False,
        labels=["18-29", "30-39", "40-49", "50-64"],
    ).astype("string")

    df["bmi_group"] = pd.cut(
        df["bmi"],
        bins=[-float("inf"), 18.5, 25, 30, float("inf")],
        right=False,
        labels=["bajo peso", "normal", "sobrepeso", "obesidad"],
    ).astype("string")

    df["children_group"] = pd.cut(
        df["children"],
        bins=[-1, 0, 2, float("inf")],
        right=True,
        labels=["0", "1-2", "3+"],
    ).astype("string")

    original_quasi = ["age", "sex", "bmi", "children", "region"]
    original_sizes = df.groupby(original_quasi, dropna=False).size()
    original_k = int(original_sizes.min())
    original_unique_records = int((original_sizes == 1).sum())

    def analyze_scheme(quasi_identifiers):
        class_sizes = df.groupby(quasi_identifiers, dropna=False).size()
        published_mask = df.set_index(quasi_identifiers).index.map(
            lambda values: class_sizes.loc[values] >= k
        )

        published = df.loc[published_mask].copy()
        published_sizes = published.groupby(
            quasi_identifiers,
            dropna=False,
        ).size()

        smoker_diversity = (
            published.groupby(quasi_identifiers, dropna=False)["smoker"]
            .nunique()
        )
        classes_without_diversity = int(
            (smoker_diversity == 1).sum()
        )
        records_without_diversity = int(
            published_sizes.loc[smoker_diversity.index[smoker_diversity == 1]].sum()
        )

        return {
            "quasi_identifiers": quasi_identifiers,
            "equivalence_classes": int(len(class_sizes)),
            "k_before_suppression": int(class_sizes.min()),
            "suppressed_records": int(len(df) - len(published)),
            "published_records": int(len(published)),
            "published_classes": int(len(published_sizes)),
            "classes_without_smoker_diversity": classes_without_diversity,
            "records_without_smoker_diversity": records_without_diversity,
        }, published

    with_children = [
        "age_group",
        "sex",
        "bmi_group",
        "children_group",
        "region",
    ]
    without_children = ["age_group", "sex", "bmi_group", "region"]

    with_children_report, with_children_published = analyze_scheme(with_children)
    without_children_report, without_children_published = analyze_scheme(without_children)

    selected_name = (
        "without_children"
        if without_children_report["suppressed_records"]
        <= with_children_report["suppressed_records"]
        else "with_children"
    )
    selected_published = (
        without_children_published
        if selected_name == "without_children"
        else with_children_published
    )
    selected_quasi = (
        without_children
        if selected_name == "without_children"
        else with_children
    )

    report = {
        "original_k": original_k,
        "original_unique_records": original_unique_records,
        "schemes": {
            "with_children": with_children_report,
            "without_children": without_children_report,
        },
        "selected_scheme": selected_name,
        "mean_charges_original": float(df["charges"].mean()),
        "mean_charges_published": float(selected_published["charges"].mean()),
        "smoker_rate_original": float((df["smoker"] == "yes").mean()),
        "smoker_rate_published": float(
            (selected_published["smoker"] == "yes").mean()
        ),
    }

    submission_columns = selected_quasi + ["smoker", "charges"]
    selected_published = selected_published[submission_columns].copy()

    (submission_dir / "privacy_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=4),
        encoding="utf-8",
    )
    selected_published.to_csv(
        submission_dir / "insurance_published.csv",
        index=False,
    )

    return report
