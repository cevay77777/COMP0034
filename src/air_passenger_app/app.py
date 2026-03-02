"""
Singapore Air Passenger Departures Dashboard
A Plotly Dash web application visualising Singapore outbound air passenger
data from 1961 to 2020.
"""

import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, callback

from air_passenger_app.data_loader import (
    load_global_departures,
    load_by_region,
    load_by_country,
    compute_yoy_growth,
    get_available_regions,
    get_available_countries,
)

# ---------------------------------------------------------------------------
# Load data at startup
# ---------------------------------------------------------------------------
df_global = load_global_departures()
df_region = load_by_region()
df_country = load_by_country()
df_yoy = compute_yoy_growth(df_global)

all_regions = get_available_regions(df_region)
all_countries = get_available_countries(df_country)

YEAR_MIN = int(df_global["year"].min())
YEAR_MAX = int(df_global["year"].max())

REGION_COLOURS = px.colors.qualitative.Bold

# ---------------------------------------------------------------------------
# App initialisation
# ---------------------------------------------------------------------------
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True,
)
app.title = "Singapore Air Passenger Departures"

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
def make_filter_panel():
    return dbc.Card(
        dbc.CardBody([
            html.H5("Filters", className="card-title fw-bold"),
            html.Hr(),
            html.Label("Year Range", className="fw-semibold"),
            dcc.RangeSlider(
                id="year-slider",
                min=YEAR_MIN,
                max=YEAR_MAX,
                step=1,
                value=[YEAR_MIN, YEAR_MAX],
                marks={y: str(y) for y in range(YEAR_MIN, YEAR_MAX + 1, 10)},
                tooltip={"placement": "bottom", "always_visible": True},
            ),
            html.Br(),
            html.Label("Region(s)", className="fw-semibold"),
            dcc.Dropdown(
                id="region-dropdown",
                options=[{"label": r, "value": r} for r in all_regions],
                value=all_regions,
                multi=True,
                placeholder="Select region(s)...",
            ),
            html.Br(),
            html.Label("Country", className="fw-semibold"),
            dcc.Dropdown(
                id="country-dropdown",
                options=[{"label": c, "value": c} for c in all_countries],
                value=None,
                multi=False,
                placeholder="All countries",
                clearable=True,
            ),
        ]),
        className="shadow-sm mb-4",
    )


def make_kpi_cards():
    total = f"{int(df_global['departures'].sum()):,}"
    peak_year = int(df_yoy.loc[df_yoy["total_departures"].idxmax(), "year"])
    top_region = df_region.groupby("region")["departures"].sum().idxmax()
    return dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H6("Total Departures (all time)", className="text-muted"),
            html.H3(total, className="fw-bold text-primary"),
        ]), className="shadow-sm"), width=4),
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H6("Peak Year", className="text-muted"),
            html.H3(str(peak_year), className="fw-bold text-success"),
        ]), className="shadow-sm"), width=4),
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H6("Top Destination Region", className="text-muted"),
            html.H3(top_region, className="fw-bold text-warning"),
        ]), className="shadow-sm"), width=4),
    ], className="mb-4")


app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.Div([
        html.H1("Singapore Air Passenger Departures",
                className="display-5 fw-bold text-primary mt-4"),
        html.P(
            "Explore outbound air passenger trends from Singapore (1961-2020).",
            className="lead text-muted",
        ),
        html.Hr(),
    ]))),
    make_kpi_cards(),
    dbc.Row([
        dbc.Col(make_filter_panel(), width=3),
        dbc.Col([
            dbc.Tabs([
                dbc.Tab(label="Global Trend", tab_id="tab-global"),
                dbc.Tab(label="By Region", tab_id="tab-region"),
                dbc.Tab(label="Year-on-Year Growth", tab_id="tab-yoy"),
                dbc.Tab(label="Seasonal Pattern", tab_id="tab-seasonal"),
                dbc.Tab(label="Country Map", tab_id="tab-map"),
            ], id="chart-tabs", active_tab="tab-global"),
            html.Div(id="tab-content", className="mt-3"),
        ], width=9),
    ]),
    html.Hr(),
    html.P(
        "Data source: Singapore Department of Statistics via data.gov.sg",
        className="text-muted text-center small mb-4",
    ),
], fluid=True)


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------

@callback(
    Output("tab-content", "children"),
    Input("chart-tabs", "active_tab"),
    Input("year-slider", "value"),
    Input("region-dropdown", "value"),
    Input("country-dropdown", "value"),
)
def render_tab(active_tab, year_range, regions, country):
    """Render the chart for the selected tab, filtered by user selections."""
    year_start, year_end = year_range

    if active_tab == "tab-global":
        return _render_global_trend(year_start, year_end)
    elif active_tab == "tab-region":
        return _render_region_bar(year_start, year_end, regions)
    elif active_tab == "tab-yoy":
        return _render_yoy(year_start, year_end)
    elif active_tab == "tab-seasonal":
        return _render_seasonal(year_start, year_end)
    elif active_tab == "tab-map":
        return _render_map(year_start, year_end, country)
    return html.P("Select a tab above.")


def _render_global_trend(year_start, year_end):
    mask = (df_global["year"] >= year_start) & (df_global["year"] <= year_end)
    fig = px.line(
        df_global[mask],
        x="date",
        y="departures",
        title="Total Monthly Air Passenger Departures from Singapore",
        labels={"date": "Date", "departures": "Passengers"},
        color_discrete_sequence=["#0d6efd"],
    )
    fig.update_traces(line_width=1.5)
    fig.update_layout(hovermode="x unified", template="plotly_white")
    return dcc.Graph(figure=fig, id="global-line-chart")


def _render_region_bar(year_start, year_end, regions):
    if not regions:
        regions = all_regions
    mask = (
        (df_region["year"] >= year_start)
        & (df_region["year"] <= year_end)
        & (df_region["region"].isin(regions))
    )
    annual = df_region[mask].groupby(["year", "region"])["departures"].sum().reset_index()
    fig = px.bar(
        annual,
        x="year",
        y="departures",
        color="region",
        title="Annual Departures by Destination Region",
        labels={"year": "Year", "departures": "Passengers", "region": "Region"},
        color_discrete_sequence=REGION_COLOURS,
        barmode="stack",
    )
    fig.update_layout(template="plotly_white", legend_title="Region")
    return dcc.Graph(figure=fig, id="region-bar-chart")


def _render_yoy(year_start, year_end):
    """Year-on-year growth chart — original chart not based on lecture materials."""
    mask = (df_yoy["year"] >= year_start) & (df_yoy["year"] <= year_end)
    filtered = df_yoy[mask].dropna(subset=["yoy_growth"])
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=filtered["year"],
        y=filtered["yoy_growth"],
        marker_color=["#198754" if v >= 0 else "#dc3545" for v in filtered["yoy_growth"]],
        hovertemplate="Year: %{x}<br>Growth: %{y:.1f}%<extra></extra>",
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="grey")
    fig.update_layout(
        title="Year-on-Year Growth in Air Passenger Departures (%)",
        xaxis_title="Year",
        yaxis_title="Growth (%)",
        template="plotly_white",
    )
    return dcc.Graph(figure=fig, id="yoy-chart")


def _render_seasonal(year_start, year_end):
    mask = (df_global["year"] >= year_start) & (df_global["year"] <= year_end)
    seasonal = df_global[mask].groupby("month")["departures"].mean().reset_index()
    month_names = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
    }
    seasonal["month_name"] = seasonal["month"].map(month_names)
    fig = px.bar(
        seasonal,
        x="month_name",
        y="departures",
        title="Average Monthly Departures — Seasonal Pattern",
        labels={"month_name": "Month", "departures": "Avg Passengers"},
        color="departures",
        color_continuous_scale="Blues",
    )
    fig.update_layout(
        template="plotly_white",
        xaxis={"categoryorder": "array", "categoryarray": list(month_names.values())},
    )
    return dcc.Graph(figure=fig, id="seasonal-chart")


def _render_map(year_start, year_end, country):
    mask = (df_country["year"] >= year_start) & (df_country["year"] <= year_end)
    if country:
        mask &= df_country["country"] == country
    totals = df_country[mask].groupby("country")["departures"].sum().reset_index()

    # Map country names to ISO-3 codes
    # Source: ISO 3166-1 alpha-3 standard
    country_iso = {
        "Malaysia": "MYS", "Indonesia": "IDN", "Thailand": "THA",
        "Philippines": "PHL", "Australia": "AUS", "Japan": "JPN",
        "Hong Kong": "HKG", "Taiwan": "TWN", "India": "IND",
        "United Kingdom": "GBR", "United States Of America": "USA",
    }
    totals["iso"] = totals["country"].map(country_iso)
    totals = totals.dropna(subset=["iso"])

    fig = px.choropleth(
        totals,
        locations="iso",
        color="departures",
        hover_name="country",
        color_continuous_scale="YlOrRd",
        title="Total Air Passenger Departures by Destination Country",
        labels={"departures": "Total Passengers"},
    )
    fig.update_layout(geo=dict(showframe=False, showcoastlines=True), template="plotly_white")
    return dcc.Graph(figure=fig, id="country-map")


if __name__ == "__main__":
    app.run(debug=True)
