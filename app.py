import streamlit as st
import pandas as pd
import plotly.express as px

from utils import (
    load_data,
    calculate_kpis,
    product_profitability,
    division_performance,
    pareto_analysis
)




st.set_page_config(
    page_title="Nassau Candy Profitability Dashboard",
    page_icon="🍬",
    layout="wide"
)




DATA_PATH = "Data/cleaned_nassau.csv"

df = load_data(DATA_PATH)



st.title("🍬 Nassau Candy Distributor")
st.subheader("Product Line Profitability & Margin Performance Analysis")

st.markdown(
    """
    This dashboard provides an interactive analysis of product,
    division and profitability performance for Nassau Candy Distributor.
    """
)




st.sidebar.header("Dashboard Filters")

min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()

date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)


divisions = sorted(df["Division"].dropna().unique())

selected_divisions = st.sidebar.multiselect(
    "Division",
    divisions,
    default=divisions
)


margin_threshold = st.sidebar.slider(
    "Minimum Gross Margin (%)",
    min_value=0,
    max_value=100,
    value=0
)

product_search = st.sidebar.text_input(
    "Search Product"
)




filtered_df = df.copy()

if len(date_range) == 2:

    filtered_df = filtered_df[
        (filtered_df["Order Date"].dt.date >= date_range[0]) &
        (filtered_df["Order Date"].dt.date <= date_range[1])
    ]

filtered_df = filtered_df[
    filtered_df["Division"].isin(selected_divisions)
]

filtered_df = filtered_df[
    filtered_df["Gross Margin %"] >= margin_threshold
]

if product_search:

    filtered_df = filtered_df[
        filtered_df["Product Name"]
        .str.contains(
            product_search,
            case=False,
            na=False
        )
    ]




kpis = calculate_kpis(filtered_df)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Revenue",
        f"${kpis['sales']:,.0f}"
    )

with col2:
    st.metric(
        "Gross Profit",
        f"${kpis['profit']:,.0f}"
    )

with col3:
    st.metric(
        "Gross Margin",
        f"{kpis['margin']:.2f}%"
    )

with col4:
    st.metric(
        "Total Units",
        f"{kpis['units']:,.0f}"
    )

with col5:
    st.metric(
        "Orders",
        f"{kpis['orders']:,}"
    )


st.divider()




st.header("1. Product Profitability Overview")

product = product_profitability(filtered_df)


col1, col2 = st.columns(2)



with col1:

    top_products = (
        product
        .sort_values("Gross_Profit", ascending=False)
        .head(10)
    )

    fig = px.bar(
        top_products,
        x="Gross_Profit",
        y="Product Name",
        orientation="h",
        title="Top 10 Products by Gross Profit"
    )

    fig.update_layout(
        yaxis=dict(categoryorder="total ascending")
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )



with col2:

    top_margin = (
        product
        .sort_values("Gross Margin %", ascending=False)
        .head(10)
    )

    fig = px.bar(
        top_margin,
        x="Gross Margin %",
        y="Product Name",
        orientation="h",
        title="Top 10 Products by Gross Margin"
    )

    fig.update_layout(
        yaxis=dict(categoryorder="total ascending")
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )




st.subheader("Product Profitability Leaderboard")

product_display = product.sort_values(
    "Gross_Profit",
    ascending=False
).copy()

product_display = product_display.rename(
    columns={
        "Gross_Profit": "Gross Profit"
    }
)

st.dataframe(
    product_display,
    use_container_width=True,
    hide_index=True
)




st.header("2. Division Performance Dashboard")

division = division_performance(filtered_df)

col1, col2 = st.columns(2)



with col1:

    division_long = division.melt(
        id_vars="Division",
        value_vars=["Sales", "Gross_Profit"],
        var_name="Metric",
        value_name="Value"
    )

    division_long["Metric"] = division_long["Metric"].replace(
        {
            "Sales": "Revenue",
            "Gross_Profit": "Gross Profit"
        }
    )

    fig = px.bar(
        division_long,
        x="Division",
        y="Value",
        color="Metric",
        barmode="group",
        title="Revenue vs Gross Profit by Division"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )



with col2:

    fig = px.bar(
        division,
        x="Division",
        y="Gross Margin %",
        title="Gross Margin by Division"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


st.subheader("Division Performance Table")

st.dataframe(
    division,
    use_container_width=True,
    hide_index=True
)




st.header("3. Cost vs Margin Diagnostics")

fig = px.scatter(
    filtered_df,
    x="Sales",
    y="Cost",
    size="Gross Profit",
    color="Gross Margin %",
    hover_name="Product Name",
    title="Cost vs Sales by Product"
)

st.plotly_chart(
    fig,
    use_container_width=True
)




st.subheader("Margin Risk Products")

risk_products = product[
    product["Gross Margin %"] < 20
].sort_values(
    "Gross Margin %"
)

st.dataframe(
    risk_products,
    use_container_width=True,
    hide_index=True
)




st.header("4. Profit Concentration Analysis")

pareto = pareto_analysis(filtered_df)

fig = px.line(
    pareto,
    x="Cumulative Product %",
    y="Cumulative Profit %",
    markers=True,
    title="Pareto Analysis – Cumulative Profit Contribution"
)

fig.add_hline(
    y=80,
    line_dash="dash",
    annotation_text="80% Profit"
)

fig.add_vline(
    x=20,
    line_dash="dash",
    annotation_text="20% Products"
)

st.plotly_chart(
    fig,
    use_container_width=True
)




st.header("Key Business Insights")

if not product.empty:

    best_product = product.loc[
        product["Gross_Profit"].idxmax(),
        "Product Name"
    ]

    best_division = division.loc[
        division["Gross_Profit"].idxmax(),
        "Division"
    ]

    highest_margin_division = division.loc[
        division["Gross Margin %"].idxmax(),
        "Division"
    ]

    st.markdown(
        f"""
        - **Most profitable product:** {best_product}
        - **Most profitable division:** {best_division}
        - **Highest-margin division:** {highest_margin_division}
        - **Overall gross margin:** {kpis['margin']:.2f}%
        """
    )




st.divider()

st.caption(
    "Nassau Candy Distributor | Product Profitability & Margin Analysis"
)