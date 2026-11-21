import pandas as pd


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Una cadena de suministros de oficina vende mucho, pero la gerencia
    sospecha que parte de esas ventas no deja utilidad. El archivo
    `data/superstore_orders.csv.gz` tiene una fila por línea de pedido, con
    el número de pedido (`Order ID`), las ventas (`Sales`), la utilidad
    (`Profit`), el descuento aplicado (`Discount`, como proporción), el
    segmento del cliente (`Customer Segment`) y la categoría del producto
    (`Product Category`). Una utilidad negativa significa que la línea se
    vendió con pérdida.

    Use estas definiciones:

    - Margen (`profit_margin`): utilidad sobre ventas.
    - Línea con pérdida: una línea cuya utilidad es negativa.
    - `loss_line_rate`: la proporción de líneas con pérdida.
    - `lost_profit`: la suma de las pérdidas de las líneas con pérdida,
      escrita como número positivo.
    - Rango de descuento (`discount_band`): `0%` si no hubo descuento,
      `1%-5%` si fue mayor que 0 y hasta 5 %, `6%-10%` si fue mayor que 5 % y
      hasta 10 %, y `más de 10%` en otro caso.

    Genere tres archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `profitability_summary.csv`, con una sola fila: `lines` (cantidad de
       líneas), `orders` (pedidos distintos), `sales`, `profit`,
       `profit_margin`, `loss_lines` (cantidad de líneas con pérdida),
       `loss_line_rate` y `lost_profit`.

    2. `discount_summary.csv`, con una fila por rango de descuento, en el
       orden en que se definieron arriba: `discount_band`, `lines`, `sales`,
       `profit`, `profit_margin`, `loss_line_rate` y `lost_profit`.

    3. `priority_segments.csv`, con los cinco segmentos segmento–categoría
       que más utilidad pierden: `Customer Segment`, `Product Category`,
       `lines`, `sales`, `profit`, `profit_margin` y `lost_profit`. Considere
       solamente segmentos con al menos 100 líneas y ordénelos por
       `lost_profit` de mayor a menor.

    La función también debe retornar las tres tablas, en el mismo orden.

    Ejemplo del formato de `discount_summary.csv`:

        discount_band,lines,sales,profit,profit_margin,loss_line_rate,...
        0%,166,170539.05,29472.3789,0.1728,0.488,...
        ...
    """

    from pathlib import Path

    activity_dir = Path(__file__).resolve().parents[1]
    data_path = activity_dir / "data" / "superstore_orders.csv.gz"
    submission_dir = activity_dir / "submission"
    submission_dir.mkdir(parents=True, exist_ok=True)

    data = pd.read_csv(
        data_path,
        sep=";",
        decimal=",",
        encoding="utf-8-sig",
    )

    data["loss_line"] = data["Profit"] < 0
    data["lost_profit"] = data["Profit"].clip(upper=0).abs()

    lines = int(len(data))
    orders = int(data["Order ID"].nunique())
    sales = float(data["Sales"].sum())
    profit = float(data["Profit"].sum())
    loss_lines = int(data["loss_line"].sum())

    profitability_summary = pd.DataFrame(
        [
            {
                "lines": lines,
                "orders": orders,
                "sales": sales,
                "profit": profit,
                "profit_margin": profit / sales,
                "loss_lines": loss_lines,
                "loss_line_rate": loss_lines / lines,
                "lost_profit": float(data["lost_profit"].sum()),
            }
        ]
    )

    def assign_discount_band(discount):
        if discount == 0:
            return "0%"
        if discount <= 0.05:
            return "1%-5%"
        if discount <= 0.10:
            return "6%-10%"
        return "más de 10%"

    data["discount_band"] = data["Discount"].map(assign_discount_band)
    discount_order = ["0%", "1%-5%", "6%-10%", "más de 10%"]

    discount_rows = []
    for discount_band in discount_order:
        band = data[data["discount_band"] == discount_band]
        band_lines = int(len(band))
        band_sales = float(band["Sales"].sum())
        band_profit = float(band["Profit"].sum())
        discount_rows.append(
            {
                "discount_band": discount_band,
                "lines": band_lines,
                "sales": band_sales,
                "profit": band_profit,
                "profit_margin": band_profit / band_sales,
                "loss_line_rate": float(band["loss_line"].mean()),
                "lost_profit": float(band["lost_profit"].sum()),
            }
        )

    discount_summary = pd.DataFrame(discount_rows)

    segment_category = (
        data.groupby(["Customer Segment", "Product Category"], as_index=False)
        .agg(
            lines=("Profit", "size"),
            sales=("Sales", "sum"),
            profit=("Profit", "sum"),
            lost_profit=("lost_profit", "sum"),
        )
    )
    segment_category = segment_category[segment_category["lines"] >= 100].copy()
    segment_category["profit_margin"] = (
        segment_category["profit"] / segment_category["sales"]
    )
    priority_segments = (
        segment_category.sort_values(
            ["lost_profit", "Customer Segment", "Product Category"],
            ascending=[False, True, True],
        )
        .head(5)
        [
            [
                "Customer Segment",
                "Product Category",
                "lines",
                "sales",
                "profit",
                "profit_margin",
                "lost_profit",
            ]
        ]
        .reset_index(drop=True)
    )

    profitability_summary.to_csv(
        submission_dir / "profitability_summary.csv",
        index=False,
    )
    discount_summary.to_csv(
        submission_dir / "discount_summary.csv",
        index=False,
    )
    priority_segments.to_csv(
        submission_dir / "priority_segments.csv",
        index=False,
    )

    return profitability_summary, discount_summary, priority_segments
