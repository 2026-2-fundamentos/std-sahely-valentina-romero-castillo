import pandas as pd


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Una entidad pública recibe peticiones, quejas, reclamos y sugerencias
    (PQRS) por dos canales, la página web y las cartas, y la ley le da 15 días
    hábiles para responder cada una. Su tarea es medir si la entidad cumple
    ese plazo.

    Los archivos `data/historical_requests_web.csv.gz` y
    `data/historical_requests_letter.csv.gz` tienen una fila por solicitud
    recibida entre 2016 y 2021 por cada canal, con su identificador
    (`record_id`), la fecha de entrada (`in_date`), el día de la semana de
    entrada (`day_name`) y la fecha de respuesta (`out_date`). Si `out_date`
    está vacía, la solicitud todavía no ha sido respondida.

    Tenga en cuenta lo siguiente:

    - Algunas solicitudes aparecen repetidas: elimine las filas idénticas
      dentro de cada canal, para contar cada solicitud una sola vez. Las
      filas sin `record_id` son solicitudes válidas.
    - Llame `letter` al canal de las cartas y `web` al de la página web.
    - Los días hábiles de respuesta son los días de lunes a viernes
      posteriores a la fecha de entrada, hasta la fecha de respuesta
      incluida. Por ejemplo, una solicitud que entra un viernes y se responde
      el lunes siguiente tardó 1 día hábil. No considere los festivos.
    - Los días calendario de respuesta son la diferencia entre la fecha de
      respuesta y la de entrada.
    - Una solicitud cumple el plazo si fue respondida en 15 días hábiles o
      menos. Una solicitud pendiente no ha cumplido el plazo.
    - `on_time_rate` es la proporción de solicitudes que cumplen el plazo,
      sobre el total de solicitudes, incluidas las pendientes.
    - Las medianas de días se calculan solamente con las solicitudes
      respondidas.

    Genere tres archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `channel_summary.csv`, con una fila por canal, en orden alfabético:
       `channel`, `requests`, `answered`, `pending`,
       `median_business_days` y `on_time_rate`.

    2. `yearly_summary.csv`, con una fila por año de entrada y canal,
       ordenada por año y luego por canal: `year`, `channel`, `requests`,
       `pending` y `on_time_rate`.

    3. `entry_day_summary.csv`, con una fila por día de entrada, de lunes a
       domingo, con los dos canales juntos: `day_name`, `requests`,
       `median_calendar_days` y `median_business_days`.

    Observe en el tercer archivo cómo cambia la lectura del tiempo de
    respuesta según se cuenten días calendario o días hábiles.

    La función también debe retornar las tres tablas, en el mismo orden.

    Ejemplo del formato de `channel_summary.csv`:

        channel,requests,answered,pending,median_business_days,on_time_rate
        letter,28138,...
        ...
    """

    from pathlib import Path

    activity_dir = Path(__file__).resolve().parents[1]
    data_dir = activity_dir / "data"
    submission_dir = activity_dir / "submission"
    submission_dir.mkdir(parents=True, exist_ok=True)

    letter = pd.read_csv(data_dir / "historical_requests_letter.csv.gz")
    web = pd.read_csv(data_dir / "historical_requests_web.csv.gz")

    letter = letter.drop_duplicates().copy()
    web = web.drop_duplicates().copy()

    letter["channel"] = "letter"
    web["channel"] = "web"
    requests = pd.concat([letter, web], ignore_index=True)

    requests["in_date"] = pd.to_datetime(
        requests["in_date"],
        format="%Y-%m-%d",
        errors="coerce",
    )
    requests["out_date"] = pd.to_datetime(
        requests["out_date"],
        format="%Y-%m-%d",
        errors="coerce",
    )
    requests["year"] = requests["in_date"].dt.year

    answered_mask = requests["out_date"].notna()

    requests["calendar_days"] = pd.NA
    requests.loc[answered_mask, "calendar_days"] = (
        requests.loc[answered_mask, "out_date"]
        - requests.loc[answered_mask, "in_date"]
    ).dt.days

    def business_days(row):
        if pd.isna(row["out_date"]):
            return pd.NA
        return pd.Timestamp(row["out_date"]).toordinal()

    requests["business_days"] = pd.NA
    requests.loc[answered_mask, "business_days"] = (
        pd.Series(
            [
                pd.bdate_range(
                    start=in_date + pd.Timedelta(days=1),
                    end=out_date,
                    freq="C",
                ).size
                for in_date, out_date in zip(
                    requests.loc[answered_mask, "in_date"],
                    requests.loc[answered_mask, "out_date"],
                )
            ],
            index=requests.loc[answered_mask].index,
        )
    )

    requests["on_time"] = (
        answered_mask
        & (requests["business_days"].astype("Float64") <= 15)
    )

    channel_summary = (
        requests.groupby("channel", as_index=False)
        .agg(
            requests=("record_id", "size"),
            answered=("out_date", lambda values: values.notna().sum()),
            pending=("out_date", lambda values: values.isna().sum()),
            median_business_days=("business_days", "median"),
            on_time_rate=("on_time", "mean"),
        )
        .sort_values("channel")
        .reset_index(drop=True)
    )

    yearly_summary = (
        requests.groupby(["year", "channel"], as_index=False)
        .agg(
            requests=("record_id", "size"),
            pending=("out_date", lambda values: values.isna().sum()),
            on_time_rate=("on_time", "mean"),
        )
        .sort_values(["year", "channel"])
        .reset_index(drop=True)
    )

    day_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    entry_day_summary = (
        requests.groupby("day_name", as_index=False)
        .agg(
            requests=("record_id", "size"),
            median_calendar_days=("calendar_days", "median"),
            median_business_days=("business_days", "median"),
        )
    )
    day_order_map = {
        day_name: position
        for position, day_name in enumerate(day_order)
    }
    entry_day_summary["_day_order"] = entry_day_summary["day_name"].map(
        day_order_map
    )
    entry_day_summary = (
        entry_day_summary.sort_values("_day_order")
        .drop(columns="_day_order")
        .reset_index(drop=True)
    )

    channel_summary.to_csv(
        submission_dir / "channel_summary.csv",
        index=False,
    )
    yearly_summary.to_csv(
        submission_dir / "yearly_summary.csv",
        index=False,
    )
    entry_day_summary.to_csv(
        submission_dir / "entry_day_summary.csv",
        index=False,
    )

    return channel_summary, yearly_summary, entry_day_summary
