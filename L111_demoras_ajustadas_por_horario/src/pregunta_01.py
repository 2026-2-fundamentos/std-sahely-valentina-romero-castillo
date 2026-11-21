import pandas as pd


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Una autoridad aeronáutica publica cada año un ranking de aerolíneas según
    su tasa de demora, y algunas aerolíneas se quejan de que es injusto: las
    demoras se acumulan a lo largo del día, de modo que una aerolínea con
    muchos vuelos en la tarde y la noche parece peor aunque opere igual de
    bien que las demás. Su tarea es construir un ranking que tenga en cuenta
    la mezcla de horarios de cada aerolínea.

    El archivo `data/flights_by_carrier_day_hour.csv.gz` tiene los vuelos
    nacionales entre 2006 y 2008, agregados por año, mes, día de la semana,
    hora programada de salida (`scheduled_departure_hour`) y aerolínea
    (`reporting_airline`). Use las columnas `operated_flights` (vuelos
    operados) y `delayed_departure_15_flights` (vuelos que salieron con 15
    minutos o más de demora).

    Siga estos pasos:

    1. Calcule la tasa nacional de demora de cada hora programada de salida:
       vuelos demorados sobre vuelos operados, con todas las aerolíneas
       juntas.
    2. Para cada aerolínea, calcule las demoras esperadas: en cada hora,
       multiplique sus vuelos operados por la tasa nacional de esa hora, y
       sume sobre todas las horas. Son las demoras que tendría si en cada hora
       se comportara como el promedio nacional.
    3. Divida las demoras observadas entre las esperadas. Un valor mayor que 1
       significa que la aerolínea se demora más de lo que explican sus
       horarios.

    Genere dos archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `hourly_delay_rates.csv`, con una fila por hora, de 0 a 23:
       `scheduled_departure_hour`, `operated_flights`,
       `delayed_departure_15_flights` y `delay_rate`.

    2. `carrier_adjusted_delays.csv`, con una fila por aerolínea:
       `reporting_airline`, `operated_flights`,
       `delayed_departure_15_flights`, `delay_rate` (la tasa sin ajustar),
       `expected_delayed_flights`, `observed_to_expected_ratio`, `crude_rank`
       y `adjusted_rank`. Incluya solamente aerolíneas con al menos 100 000
       vuelos operados. `crude_rank` es la posición según `delay_rate` y
       `adjusted_rank` la posición según `observed_to_expected_ratio`; en
       ambos, 1 es la peor aerolínea. Ordene la tabla por `adjusted_rank`.

    Compare los dos rankings: las aerolíneas que cambian de posición son las
    que el ranking sin ajustar juzga mal por sus horarios.

    La función también debe retornar las dos tablas, en el mismo orden.

    Ejemplo del formato de `carrier_adjusted_delays.csv`:

        reporting_airline,operated_flights,...,crude_rank,adjusted_rank
        EV,819223,...,1,1
        ...
    """

    from pathlib import Path

    activity_dir = Path(__file__).resolve().parents[1]
    data_path = (
        activity_dir
        / "data"
        / "flights_by_carrier_day_hour.csv.gz"
    )
    submission_dir = activity_dir / "submission"
    submission_dir.mkdir(parents=True, exist_ok=True)

    data = pd.read_csv(data_path)

    for column in (
        "operated_flights",
        "delayed_departure_15_flights",
    ):
        data[column] = pd.to_numeric(data[column], errors="coerce")

    hourly = (
        data.groupby("scheduled_departure_hour", as_index=False)
        .agg(
            operated_flights=("operated_flights", "sum"),
            delayed_departure_15_flights=("delayed_departure_15_flights", "sum"),
        )
    )
    hourly = (
        pd.DataFrame({"scheduled_departure_hour": range(24)})
        .merge(hourly, on="scheduled_departure_hour", how="left")
        .fillna({"operated_flights": 0, "delayed_departure_15_flights": 0})
    )

    hourly["delay_rate"] = (
        hourly["delayed_departure_15_flights"]
        / hourly["operated_flights"]
    )
    hourly = hourly[
        [
            "scheduled_departure_hour",
            "operated_flights",
            "delayed_departure_15_flights",
            "delay_rate",
        ]
    ]
    hourly["operated_flights"] = hourly["operated_flights"].astype("int64")
    hourly["delayed_departure_15_flights"] = (
        hourly["delayed_departure_15_flights"].astype("int64")
    )

    hourly_rates = hourly.set_index("scheduled_departure_hour")["delay_rate"]

    carriers = (
        data.groupby("reporting_airline", as_index=False)
        .agg(
            operated_flights=("operated_flights", "sum"),
            delayed_departure_15_flights=("delayed_departure_15_flights", "sum"),
        )
    )
    carriers = carriers[carriers["operated_flights"] >= 100_000].copy()
    carriers["operated_flights"] = carriers["operated_flights"].astype("int64")
    carriers["delayed_departure_15_flights"] = (
        carriers["delayed_departure_15_flights"].astype("int64")
    )
    carriers["delay_rate"] = (
        carriers["delayed_departure_15_flights"]
        / carriers["operated_flights"]
    )

    carrier_hourly = (
        data.groupby(
            ["reporting_airline", "scheduled_departure_hour"],
            as_index=False,
        )
        .agg(operated_flights=("operated_flights", "sum"))
    )
    carrier_hourly["national_delay_rate"] = carrier_hourly[
        "scheduled_departure_hour"
    ].map(hourly_rates)
    carrier_hourly["expected_delayed_flights"] = (
        carrier_hourly["operated_flights"]
        * carrier_hourly["national_delay_rate"]
    )

    expected = (
        carrier_hourly.groupby("reporting_airline", as_index=False)
        .agg(expected_delayed_flights=("expected_delayed_flights", "sum"))
    )
    carriers = carriers.merge(expected, on="reporting_airline", how="left")
    carriers["observed_to_expected_ratio"] = (
        carriers["delayed_departure_15_flights"]
        / carriers["expected_delayed_flights"]
    )

    carriers["crude_rank"] = (
        carriers["delay_rate"]
        .rank(method="min", ascending=False)
        .astype("int64")
    )
    carriers["adjusted_rank"] = (
        carriers["observed_to_expected_ratio"]
        .rank(method="min", ascending=False)
        .astype("int64")
    )

    carriers = carriers.sort_values("adjusted_rank").reset_index(drop=True)
    carriers = carriers[
        [
            "reporting_airline",
            "operated_flights",
            "delayed_departure_15_flights",
            "delay_rate",
            "expected_delayed_flights",
            "observed_to_expected_ratio",
            "crude_rank",
            "adjusted_rank",
        ]
    ]

    hourly.to_csv(
        submission_dir / "hourly_delay_rates.csv",
        index=False,
    )
    carriers.to_csv(
        submission_dir / "carrier_adjusted_delays.csv",
        index=False,
    )

    return hourly, carriers
