"""Interactive SpaceX Falcon 9 dashboard (Plotly Dash).
Run after placing dataset_part_2_DEL.csv beside this file: python spacex_dash_app.py
If the CSV is absent, the app uses the same public dataset mirror as run_analysis.py.
"""
from pathlib import Path
import requests
import pandas as pd
from io import StringIO
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

HERE = Path(__file__).resolve().parent
DATA_FILE = HERE / "dataset_part_2_DEL.csv"
DATA_URLS = [
    "https://raw.githubusercontent.com/DanielEduardoLopez/IBM-SpaceX/main/dataset_part_2_DEL.csv",
    "https://raw.githubusercontent.com/techdatapath/spacex-capstone-project/main/dataset_part_2.csv",
]

def load_data():
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
    else:
        errors = []
        for url in DATA_URLS:
            try:
                res = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
                res.raise_for_status()
                df = pd.read_csv(StringIO(res.text))
                df.to_csv(DATA_FILE, index=False)
                break
            except Exception as e:
                errors.append(str(e))
        else:
            raise RuntimeError("Cannot load course CSV. Place dataset_part_2_DEL.csv beside this app. " + " | ".join(errors))
    cols = {str(c).lower().replace("_", ""): c for c in df.columns}
    # Handle case/underscore variations.
    df = df.rename(columns={cols[k]: name for k, name in [("class", "Class"), ("launchsite", "LaunchSite"), ("payloadmass", "PayloadMass"), ("flightnumber", "FlightNumber")] if k in cols})
    needed = {"Class", "LaunchSite", "PayloadMass", "FlightNumber"}
    if not needed.issubset(df.columns):
        raise ValueError(f"CSV needs columns {sorted(needed)}; found {list(df.columns)}")
    df["Class"] = pd.to_numeric(df["Class"], errors="coerce")
    df["PayloadMass"] = pd.to_numeric(df["PayloadMass"], errors="coerce")
    df["FlightNumber"] = pd.to_numeric(df["FlightNumber"], errors="coerce")
    return df.dropna(subset=["Class", "LaunchSite", "FlightNumber"]).copy()

df = load_data()
launch_sites = sorted(df["LaunchSite"].dropna().unique().tolist())
site_options = [{"label": "All launch sites", "value": "ALL"}] + [{"label": x, "value": x} for x in launch_sites]
max_payload = float(df["PayloadMass"].max()) if df["PayloadMass"].notna().any() else 10000.0

app = Dash(__name__)
app.title = "SpaceX Falcon 9 Landing Analytics"
app.layout = html.Div([
    html.Div([
        html.H1("SpaceX Falcon 9 Landing Analytics", style={"marginBottom": "5px"}),
        html.P("Explore landing outcomes by launch site and payload mass")
    ], style={"background": "#102A43", "color": "white", "padding": "22px", "borderRadius": "10px"}),
    html.Div([
        html.Div([html.Label("Launch site", style={"fontWeight": "bold"}),
                  dcc.Dropdown(id="launch-site-dropdown", options=site_options, value="ALL", clearable=False)],
                 style={"flex": "1", "minWidth": "270px"}),
        html.Div([html.Label("Maximum payload mass (kg)", style={"fontWeight": "bold"}),
                  dcc.Slider(id="payload-slider", min=0, max=max(1000, max_payload), step=500,
                             value=max_payload, marks={0: "0", int(max_payload): f"{int(max_payload):,}"},
                             tooltip={"placement": "bottom", "always_visible": True})],
                 style={"flex": "2", "minWidth": "300px", "padding": "12px 10px"})
    ], style={"display": "flex", "gap": "24px", "flexWrap": "wrap", "margin": "20px 0"}),
    html.Div(id="kpi-row", style={"display": "flex", "gap": "14px", "flexWrap": "wrap", "marginBottom": "15px"}),
    html.Div([
        html.Div(dcc.Graph(id="success-pie"), style={"flex": "1 1 45%", "minWidth": "350px"}),
        html.Div(dcc.Graph(id="payload-scatter"), style={"flex": "1 1 45%", "minWidth": "350px"})
    ], style={"display": "flex", "gap": "18px", "flexWrap": "wrap"}),
    html.Footer("Data: historical SpaceX Falcon 9 course dataset. Interpret relationships as associations, not causation.",
                style={"color": "#52606D", "paddingTop": "12px"})
], style={"fontFamily": "Arial, sans-serif", "background": "#F0F4F8", "padding": "22px", "color": "#243B53"})

@app.callback(
    Output("success-pie", "figure"), Output("payload-scatter", "figure"), Output("kpi-row", "children"),
    Input("launch-site-dropdown", "value"), Input("payload-slider", "value")
)
def update_dashboard(site, max_mass):
    data = df.copy()
    if site and site != "ALL":
        data = data[data["LaunchSite"] == site]
    payload_filtered = data[data["PayloadMass"].isna() | (data["PayloadMass"] <= (max_mass or max_payload))]
    counts = data["Class"].astype(int).map({0: "Unsuccessful landing", 1: "Successful landing"}).value_counts().reindex(
        ["Successful landing", "Unsuccessful landing"], fill_value=0).reset_index()
    counts.columns = ["Outcome", "Records"]
    pie = px.pie(counts, names="Outcome", values="Records", hole=0.55, title="Landing Outcome Distribution",
                 color="Outcome", color_discrete_map={"Successful landing": "#2A9D8F", "Unsuccessful landing": "#E76F51"})
    pie.update_layout(template="plotly_white", legend_title="Outcome")
    color_col = "BoosterVersion" if "BoosterVersion" in payload_filtered.columns else "LaunchSite"
    scatter = px.scatter(payload_filtered.dropna(subset=["PayloadMass"]), x="PayloadMass", y="Class",
                         color=color_col, hover_data=[c for c in ["FlightNumber", "LaunchSite", "Orbit"] if c in payload_filtered.columns],
                         title="Payload Mass vs. Landing Outcome", labels={"Class": "Landing outcome (0 = no, 1 = yes)", "PayloadMass": "Payload mass (kg)"})
    scatter.update_yaxes(tickmode="array", tickvals=[0, 1], ticktext=["Unsuccessful", "Successful"])
    scatter.update_layout(template="plotly_white")
    pct = float(data["Class"].mean() * 100) if len(data) else 0.0
    kpis = [
        html.Div([html.Div("Launch records", style={"fontSize": "13px"}), html.H3(f"{len(data):,}")],
                 style={"background": "white", "padding": "12px 18px", "borderRadius": "8px", "minWidth": "150px"}),
        html.Div([html.Div("Landing success rate", style={"fontSize": "13px"}), html.H3(f"{pct:.1f}%")],
                 style={"background": "white", "padding": "12px 18px", "borderRadius": "8px", "minWidth": "170px"}),
        html.Div([html.Div("Rows within payload filter", style={"fontSize": "13px"}), html.H3(f"{len(payload_filtered):,}")],
                 style={"background": "white", "padding": "12px 18px", "borderRadius": "8px", "minWidth": "180px"}),
    ]
    return pie, scatter, kpis

if __name__ == "__main__":
    app.run(debug=False)
