from pathlib import Path

import pandas as pd


def pregunta_01():
    """
    Las frases de este laboratorio no están en una tabla, sino en miles de
    archivos de texto organizados en carpetas. Dentro de `data/` hay dos
    carpetas, `train/` y `test/`, y cada una contiene las carpetas
    `negative/`, `neutral/` y `positive/`. Cada archivo `.txt` contiene una
    frase, y la carpeta donde se encuentra indica su sentimiento.

    Su tarea es construir un dataset para cada división y guardarlo en:

    - `submission/train_dataset.csv`
    - `submission/test_dataset.csv`

    Cada archivo debe tener dos columnas: `phrase`, con el texto de la frase,
    y `target`, con el nombre de la carpeta de sentimiento (`negative`,
    `neutral` o `positive`). Recorra las carpetas y los archivos en orden
    alfabético, de modo que el resultado sea siempre el mismo. No guarde el
    índice de Pandas en el CSV.

    Ejemplo del formato de cada archivo:

        phrase,target
        "The real estate company posted a net loss ...",negative
        ...
        "Cardona slowed her vehicle , turned around ...",neutral
        ...
    """

    activity_dir = Path(__file__).resolve().parents[1]
    data_dir = activity_dir / "data"
    submission_dir = activity_dir / "submission"
    submission_dir.mkdir(parents=True, exist_ok=True)

    targets = ("negative", "neutral", "positive")

    for split in ("train", "test"):
        phrases = []
        labels = []

        for target in targets:
            target_dir = data_dir / split / target
            for text_file in sorted(target_dir.glob("*.txt")):
                phrases.append(text_file.read_text(encoding="utf-8").strip())
                labels.append(target)

        dataset = pd.DataFrame({"phrase": phrases, "target": labels})
        dataset.to_csv(
            submission_dir / f"{split}_dataset.csv",
            index=False,
        )
