import pandas as pd


def build_cohort_analysis() -> pd.DataFrame:
    """
    Una tienda quiere saber si sus clientes vuelven a comprar después de su
    primera compra. Para responder, agrupe a los clientes en cohortes según
    el mes de su primera compra y mida, mes a mes, qué proporción de cada
    cohorte vuelve a comprar. Use `data/sales.csv.gz`, que tiene una fila por
    orden con su cliente (`CustomerID`) y su fecha (`OrderDate`).

    Use estas definiciones:

    - `cohort_month`: el mes de la primera compra del cliente, escrito como
      `AAAA-MM`.
    - `period_index`: los meses transcurridos desde `cohort_month`; es 0 en el
      mes de la primera compra, 1 en el mes siguiente, y así sucesivamente.
    - `active_customers`: la cantidad de clientes distintos de la cohorte que
      compraron en ese período.
    - `cohort_size`: la cantidad de clientes de la cohorte, es decir, sus
      clientes activos en el período 0.
    - `retention_rate`: `active_customers` sobre `cohort_size`.

    Genere dos archivos en `submission/`:

    1. `cohort_retention.csv`, sin el índice de Pandas, con las columnas
       `cohort_month`, `period_index`, `active_customers`, `cohort_size` y
       `retention_rate`, y una fila por cada combinación cohorte–período
       observada, ordenadas por cohorte y período.

    2. `cohort_retention_heatmap.png`, un mapa de calor de `retention_rate`
       con una fila por cohorte (eje vertical) y una columna por período
       (eje horizontal). Muestre los valores como porcentajes. Los períodos
       que todavía no se pueden observar para una cohorte no significan
       retención cero: déjelos vacíos en el mapa.

    La función también debe retornar la tabla de retención.

    Ejemplo del formato de `cohort_retention.csv`:

        cohort_month,period_index,active_customers,cohort_size,retention_rate
        2022-01,0,100,100,1.0
        2022-01,1,26,100,0.26
        ...
    """

    from pathlib import Path

    activity_dir = Path(__file__).resolve().parents[1]
    data_path = activity_dir / "data" / "sales.csv.gz"
    submission_dir = activity_dir / "submission"
    submission_dir.mkdir(parents=True, exist_ok=True)

    sales = pd.read_csv(data_path)

    sales["order_month"] = pd.to_datetime(
        sales["OrderDate"],
        errors="coerce",
    ).dt.to_period("M")

    sales["cohort_month"] = (
        sales.groupby("CustomerID")["order_month"].transform("min")
    )

    cohort_month_number = sales["cohort_month"].dt.year * 12 + sales[
        "cohort_month"
    ].dt.month - 1
    order_month_number = sales["order_month"].dt.year * 12 + sales[
        "order_month"
    ].dt.month - 1
    sales["period_index"] = order_month_number - cohort_month_number

    active = (
        sales.groupby(["cohort_month", "period_index"], as_index=False)
        .agg(active_customers=("CustomerID", "nunique"))
    )

    cohort_sizes = (
        active[active["period_index"] == 0]
        .set_index("cohort_month")["active_customers"]
    )
    active["cohort_size"] = active["cohort_month"].map(cohort_sizes)
    active["retention_rate"] = (
        active["active_customers"] / active["cohort_size"]
    )

    active = active[
        [
            "cohort_month",
            "period_index",
            "active_customers",
            "cohort_size",
            "retention_rate",
        ]
    ].sort_values(["cohort_month", "period_index"]).reset_index(drop=True)

    active["cohort_month"] = active["cohort_month"].astype(str)
    active["period_index"] = active["period_index"].astype("int64")

    active.to_csv(
        submission_dir / "cohort_retention.csv",
        index=False,
    )

    heatmap = active.pivot(
        index="cohort_month",
        columns="period_index",
        values="retention_rate",
    )

    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter

    fig, axis = plt.subplots(figsize=(10, 6))
    image = axis.imshow(
        heatmap.to_numpy(dtype=float),
        aspect="auto",
        cmap="Blues",
        vmin=0,
        vmax=1,
    )

    axis.set_xticks(range(len(heatmap.columns)))
    axis.set_xticklabels(heatmap.columns)
    axis.set_yticks(range(len(heatmap.index)))
    axis.set_yticklabels(heatmap.index)
    axis.set_xlabel("Period index")
    axis.set_ylabel("Cohort month")

    for row_index in range(len(heatmap.index)):
        for column_index in range(len(heatmap.columns)):
            value = heatmap.iloc[row_index, column_index]
            if pd.notna(value):
                axis.text(
                    column_index,
                    row_index,
                    f"{value:.0%}",
                    ha="center",
                    va="center",
                )

    axis.set_title("Cohort retention")
    fig.colorbar(
        image,
        ax=axis,
        label="Retention rate",
        format=PercentFormatter(1.0),
    )
    fig.tight_layout()
    fig.savefig(
        submission_dir / "cohort_retention_heatmap.png",
        dpi=150,
    )
    plt.close(fig)

    return active
