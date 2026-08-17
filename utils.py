import pandas as pd
import numpy as np


def load_data(file_path):
    """Load and prepare the cleaned Nassau Candy dataset."""
    
    df = pd.read_csv(file_path)

    
    df["Order Date"] = pd.to_datetime(
        df["Order Date"],
        errors="coerce"
    )

    
    df.columns = df.columns.str.strip()

    
    if "Gross Margin %" not in df.columns:
        df["Gross Margin %"] = np.where(
            df["Sales"] != 0,
            (df["Gross Profit"] / df["Sales"]) * 100,
            0
        )

    if "Profit per Unit" not in df.columns:
        df["Profit per Unit"] = np.where(
            df["Units"] != 0,
            df["Gross Profit"] / df["Units"],
            0
        )

    return df


def calculate_kpis(df):
    """Calculate main dashboard KPIs."""

    total_sales = df["Sales"].sum()
    total_profit = df["Gross Profit"].sum()
    total_units = df["Units"].sum()
    total_orders = df["Order ID"].nunique()

    gross_margin = (
        total_profit / total_sales * 100
        if total_sales != 0 else 0
    )

    profit_per_unit = (
        total_profit / total_units
        if total_units != 0 else 0
    )

    return {
        "sales": total_sales,
        "profit": total_profit,
        "margin": gross_margin,
        "units": total_units,
        "orders": total_orders,
        "profit_per_unit": profit_per_unit
    }


def product_profitability(df):
    """Calculate product-level profitability."""

    product = (
        df.groupby("Product Name")
        .agg(
            Sales=("Sales", "sum"),
            Units=("Units", "sum"),
            Gross_Profit=("Gross Profit", "sum"),
            Cost=("Cost", "sum")
        )
        .reset_index()
    )

    product["Gross Margin %"] = np.where(
        product["Sales"] != 0,
        product["Gross_Profit"] / product["Sales"] * 100,
        0
    )

    product["Profit per Unit"] = np.where(
        product["Units"] != 0,
        product["Gross_Profit"] / product["Units"],
        0
    )

    return product


def division_performance(df):
    """Calculate division-level performance."""

    division = (
        df.groupby("Division")
        .agg(
            Sales=("Sales", "sum"),
            Cost=("Cost", "sum"),
            Gross_Profit=("Gross Profit", "sum"),
            Units=("Units", "sum")
        )
        .reset_index()
    )

    division["Gross Margin %"] = np.where(
        division["Sales"] != 0,
        division["Gross_Profit"] / division["Sales"] * 100,
        0
    )

    return division


def pareto_analysis(df):
    """Calculate cumulative profit contribution by product."""

    product = (
        df.groupby("Product Name")["Gross Profit"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    product["Profit Contribution %"] = (
        product["Gross Profit"] /
        product["Gross Profit"].sum()
    ) * 100

    product["Cumulative Profit %"] = (
        product["Profit Contribution %"].cumsum()
    )

    product["Cumulative Product %"] = (
        np.arange(1, len(product) + 1) /
        len(product) * 100
    )

    return product