import pandas as pd


def clean_campaign_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Los datos de una campaña de mercadeo bancario llegaron repartidos en diez
    archivos comprimidos, `data/bank-marketing-campaing-*.csv.gz`, con
    información mezclada del cliente, de la campaña y del contexto económico.
    Su tarea es leerlos directamente desde los archivos comprimidos, sin
    descomprimirlos a mano, y separarlos en tres tablas limpias.

    Guarde cada tabla como un CSV sin comprimir en `submission/`, sin el índice
    de Pandas y con las columnas en el orden indicado:

    1. `client.csv`: `client_id`, `age`, `job`, `marital`, `education`,
       `credit_default` y `mortgage`.
       - En `job`, elimine los puntos y cambie los guiones por guiones bajos.
       - En `education`, cambie los puntos por guiones bajos y deje el valor
         `unknown` como faltante.
       - En `credit_default` y `mortgage`, escriba 1 si el valor es `yes` y 0
         en cualquier otro caso.

    2. `campaign.csv`: `client_id`, `number_contacts`, `contact_duration`,
       `previous_campaign_contacts`, `previous_outcome`, `campaign_outcome` y
       `last_contact_date`.
       - En `previous_outcome`, escriba 1 si el valor es `success` y 0 en
         cualquier otro caso.
       - En `campaign_outcome`, escriba 1 si el valor es `yes` y 0 en
         cualquier otro caso.
       - Construya `last_contact_date` a partir de las columnas `month` y
         `day`, usando el año 2022 y el formato `AAAA-MM-DD`.

    3. `economics.csv`: `client_id`, `cons_price_idx` y
       `euribor_three_months`.

    La función también debe retornar las tres tablas, en el orden `client`,
    `campaign` y `economics`.

    Ejemplo del formato de `campaign.csv`:

        client_id,number_contacts,contact_duration,...,last_contact_date
        0,1,261,...,2022-05-13
        ...
    """

    from pathlib import Path

    activity_dir = Path(__file__).resolve().parents[1]
    data_dir = activity_dir / "data"
    submission_dir = activity_dir / "submission"
    submission_dir.mkdir(parents=True, exist_ok=True)

    file_paths = sorted(data_dir.glob("bank-marketing-campaing-*.csv.gz"))
    data = pd.concat(
        [pd.read_csv(file_path) for file_path in file_paths],
        ignore_index=True,
    )

    data["job"] = (
        data["job"]
        .astype("string")
        .str.replace(".", "", regex=False)
        .str.replace("-", "_", regex=False)
    )

    data["education"] = (
        data["education"]
        .astype("string")
        .str.replace(".", "_", regex=False)
        .replace("unknown", pd.NA)
    )

    data["credit_default"] = (data["credit_default"] == "yes").astype("int64")
    data["mortgage"] = (data["mortgage"] == "yes").astype("int64")
    data["previous_outcome"] = (data["previous_outcome"] == "success").astype("int64")
    data["campaign_outcome"] = (data["campaign_outcome"] == "yes").astype("int64")

    month_numbers = {
        "jan": "01",
        "feb": "02",
        "mar": "03",
        "apr": "04",
        "may": "05",
        "jun": "06",
        "jul": "07",
        "aug": "08",
        "sep": "09",
        "oct": "10",
        "nov": "11",
        "dec": "12",
    }
    data["month"] = data["month"].astype("string").str.lower().map(month_numbers)
    data["day"] = pd.to_numeric(data["day"], errors="coerce")
    data["last_contact_date"] = (
        "2022-" + data["month"] + "-" + data["day"].astype("Int64").astype("string").str.zfill(2)
    )

    client = data[
        [
            "client_id",
            "age",
            "job",
            "marital",
            "education",
            "credit_default",
            "mortgage",
        ]
    ].copy()

    campaign = data[
        [
            "client_id",
            "number_contacts",
            "contact_duration",
            "previous_campaign_contacts",
            "previous_outcome",
            "campaign_outcome",
            "last_contact_date",
        ]
    ].copy()

    economics = data[
        ["client_id", "cons_price_idx", "euribor_three_months"]
    ].copy()

    client = client.sort_values("client_id").reset_index(drop=True)
    campaign = campaign.sort_values("client_id").reset_index(drop=True)
    economics = economics.sort_values("client_id").reset_index(drop=True)

    client.to_csv(submission_dir / "client.csv", index=False)
    campaign.to_csv(submission_dir / "campaign.csv", index=False)
    economics.to_csv(submission_dir / "economics.csv", index=False)

    return client, campaign, economics
