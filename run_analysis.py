"""SpaceX Falcon 9 data-science capstone workflow.

Run from the project folder:
    python run_analysis.py

Expected input: dataset_part_2_DEL.csv (historical course dataset). If absent, the
script attempts to download a publicly available copy. If the network is blocked,
place the CSV in this folder and rerun. All charts/tables/metrics are computed from
that CSV at runtime; no model metrics are hard-coded.
"""
from __future__ import annotations
import json, sqlite3, sys
from pathlib import Path
from io import StringIO
import warnings
import requests
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             classification_report, ConfusionMatrixDisplay, roc_auc_score)
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier

warnings.filterwarnings("ignore", category=FutureWarning)
sns.set_theme(style="whitegrid", context="notebook")
BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / "outputs"
OUT_DIR.mkdir(exist_ok=True)
DATA_FILE = BASE_DIR / "dataset_part_2_DEL.csv"
DATA_URLS = [
    "https://raw.githubusercontent.com/DanielEduardoLopez/IBM-SpaceX/main/dataset_part_2_DEL.csv",
    "https://raw.githubusercontent.com/techdatapath/spacex-capstone-project/main/dataset_part_2.csv",
]


def load_course_dataset() -> pd.DataFrame:
    """Load local historical course data or download a public mirror."""
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
    else:
        errors = []
        for url in DATA_URLS:
            try:
                response = requests.get(url, timeout=25, headers={"User-Agent": "Mozilla/5.0"})
                response.raise_for_status()
                if "<html" in response.text[:500].lower():
                    raise ValueError("URL returned HTML, not CSV")
                df = pd.read_csv(StringIO(response.text))
                df.to_csv(DATA_FILE, index=False)
                print(f"Downloaded historical course data from: {url}")
                break
            except Exception as exc:
                errors.append(f"{url}: {exc}")
        else:
            raise RuntimeError(
                "Could not download the historical course dataset. Download dataset_part_2_DEL.csv "
                "from the project dataset source listed in README.md and save it beside run_analysis.py.\n" +
                "Network errors: " + " | ".join(errors)
            )
    # Normalise likely column-name variants.
    rename = {
        "class": "Class", "payloadmass": "PayloadMass", "launchsite": "LaunchSite",
        "flightnumber": "FlightNumber", "boosterversion": "BoosterVersion",
        "landingpad": "LandingPad", "reusedcount": "ReusedCount"
    }
    df = df.rename(columns={c: rename.get(str(c).replace("_", "").lower(), c) for c in df.columns})
    required = {"FlightNumber", "LaunchSite", "PayloadMass", "Class"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataset missing required columns {sorted(missing)}; columns found: {list(df.columns)}")
    df["FlightNumber"] = pd.to_numeric(df["FlightNumber"], errors="coerce")
    df["PayloadMass"] = pd.to_numeric(df["PayloadMass"], errors="coerce")
    df["Class"] = pd.to_numeric(df["Class"], errors="coerce")
    df = df.dropna(subset=["FlightNumber", "LaunchSite", "Class"]).copy()
    df["Class"] = df["Class"].astype(int)
    if not set(df["Class"].unique()).issubset({0, 1}):
        raise ValueError("Class target must contain binary 0/1 landing outcomes.")
    return df


def safe_savefig(name: str):
    plt.tight_layout()
    plt.savefig(OUT_DIR / name, dpi=180, bbox_inches="tight")
    plt.close()


def run_sql(df: pd.DataFrame) -> dict:
    db_path = OUT_DIR / "spacex_capstone.sqlite"
    with sqlite3.connect(db_path) as conn:
        df.to_sql("launches", conn, if_exists="replace", index=False)
        site = pd.read_sql_query("""
          SELECT LaunchSite, COUNT(*) AS LaunchCount,
                 ROUND(AVG(CAST(Class AS REAL))*100, 1) AS LandingSuccessPct
          FROM launches GROUP BY LaunchSite ORDER BY LaunchCount DESC
        """, conn)
        orbit = pd.read_sql_query("""
          SELECT Orbit, COUNT(*) AS LaunchCount,
                 ROUND(AVG(CAST(Class AS REAL))*100, 1) AS LandingSuccessPct
          FROM launches GROUP BY Orbit ORDER BY LaunchCount DESC
        """, conn) if "Orbit" in df.columns else pd.DataFrame()
        annual = pd.read_sql_query("""
          SELECT CAST(FlightNumber AS INTEGER) AS FlightNumber,
                 COUNT(*) AS RecordCount,
                 ROUND(AVG(CAST(Class AS REAL))*100, 1) AS LandingSuccessPct
          FROM launches GROUP BY CAST(FlightNumber AS INTEGER) ORDER BY FlightNumber
        """, conn)
    site.to_csv(OUT_DIR / "sql_launch_site_summary.csv", index=False)
    orbit.to_csv(OUT_DIR / "sql_orbit_summary.csv", index=False)
    annual.to_csv(OUT_DIR / "sql_flight_summary.csv", index=False)
    return {"site": site, "orbit": orbit, "flight": annual}


def make_eda(df: pd.DataFrame):
    # Launch site count and target success rate.
    site = df.groupby("LaunchSite", as_index=False).agg(
        LaunchCount=("Class", "size"), SuccessRate=("Class", "mean"))
    site["SuccessRatePct"] = site["SuccessRate"] * 100
    fig, ax = plt.subplots(figsize=(10, 5.5))
    sns.barplot(data=site.sort_values("LaunchCount", ascending=False), x="LaunchSite", y="LaunchCount", color="#4285F4", ax=ax)
    ax.set_title("Falcon 9 Records by Launch Site")
    ax.set_xlabel("Launch site"); ax.set_ylabel("Number of records")
    ax.tick_params(axis="x", rotation=15)
    safe_savefig("launch_site_counts.png")
    site.sort_values("LaunchCount", ascending=False).to_csv(OUT_DIR / "launch_site_summary.csv", index=False)

    # Landing outcome distribution.
    outcomes = df["Class"].value_counts().reindex([0, 1], fill_value=0)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.pie(outcomes.values, labels=["Unsuccessful (0)", "Successful (1)"], autopct="%1.1f%%",
           startangle=90, colors=["#E76F51", "#2A9D8F"], wedgeprops={"width": 0.42, "edgecolor": "white"})
    ax.set_title("Landing Outcome Distribution")
    safe_savefig("landing_outcome_pie.png")

    # Payload vs outcome scatter.
    if "PayloadMass" in df.columns:
        plot_df = df.dropna(subset=["PayloadMass"])
        fig, ax = plt.subplots(figsize=(9, 5.5))
        sns.stripplot(data=plot_df, x="Class", y="PayloadMass", hue="Class", jitter=0.23,
                      alpha=0.7, palette={0: "#E76F51", 1: "#2A9D8F"}, ax=ax, legend=False)
        ax.set_xticks([0, 1], ["Unsuccessful landing", "Successful landing"])
        ax.set_title("Payload Mass vs. Landing Outcome")
        ax.set_xlabel("Landing outcome"); ax.set_ylabel("Payload mass (kg)")
        safe_savefig("payload_vs_landing_outcome.png")

    # Flight-number trend: rolling success rate. Each flight number is normally one launch,
    # so use a rolling window to visualise the trend without presenting each 0/1 as a rate.
    ordered = df.dropna(subset=["FlightNumber"]).sort_values("FlightNumber").copy()
    window = min(10, max(3, len(ordered)//10))
    ordered["RollingSuccessRate"] = ordered["Class"].rolling(window=window, min_periods=1).mean() * 100
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(ordered["FlightNumber"], ordered["RollingSuccessRate"], color="#2463EB", linewidth=2)
    ax.set_ylim(-3, 103); ax.set_title(f"Rolling Landing Success Rate (window={window} launches)")
    ax.set_xlabel("Flight number"); ax.set_ylabel("Rolling success rate (%)")
    safe_savefig("success_trend_by_flight.png")

    if "Orbit" in df.columns:
        orbit = df.groupby("Orbit", dropna=False).agg(
            LaunchCount=("Class", "size"), SuccessRate=("Class", "mean")
        ).reset_index().sort_values("LaunchCount", ascending=False)
        orbit["Orbit"] = orbit["Orbit"].fillna("Unknown")
        orbit["SuccessRatePct"] = orbit["SuccessRate"] * 100
        orbit.to_csv(OUT_DIR / "orbit_summary.csv", index=False)
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=orbit.head(10), y="Orbit", x="LaunchCount", color="#4285F4", ax=ax)
        ax.set_title("Most Frequent Payload Orbits")
        safe_savefig("orbit_counts.png")

    # Basic missingness chart.
    missing = df.isna().sum().sort_values(ascending=False)
    missing = missing[missing > 0]
    if not missing.empty:
        fig, ax = plt.subplots(figsize=(10, 4.5))
        missing.plot(kind="bar", ax=ax, color="#F4A261")
        ax.set_title("Missing Values by Column"); ax.set_ylabel("Missing rows")
        safe_savefig("missing_values.png")


def make_map(df: pd.DataFrame):
    # Course dataset may repeat the same coordinate for each launch; collapse to sites.
    if not {"Latitude", "Longitude", "LaunchSite"}.issubset(df.columns):
        print("Map skipped: Latitude/Longitude/LaunchSite columns are unavailable.")
        return
    geo = df.dropna(subset=["Latitude", "Longitude"]).copy()
    if geo.empty:
        print("Map skipped: no valid coordinates."); return
    site = geo.groupby("LaunchSite", as_index=False).agg(
        Latitude=("Latitude", "mean"), Longitude=("Longitude", "mean"),
        Launches=("Class", "size"), SuccessPct=("Class", lambda s: round(100*s.mean(), 1)))
    fmap = folium.Map(location=[geo["Latitude"].mean(), geo["Longitude"].mean()], zoom_start=3, tiles="CartoDB positron")
    for _, row in site.iterrows():
        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]], radius=8 + min(8, row["Launches"] / 4),
            color="#1D4ED8", fill=True, fill_opacity=0.75,
            tooltip=str(row["LaunchSite"]),
            popup=(f"<b>{row['LaunchSite']}</b><br>Records: {row['Launches']}<br>Landing success: {row['SuccessPct']}%")
        ).add_to(fmap)
    # Pairwise Haversine distance analysis from coordinates contained in the dataset.
    def haversine_km(lat1, lon1, lat2, lon2):
        radius = 6371.0088
        p1, p2 = np.radians(lat1), np.radians(lat2)
        dlat = p2 - p1
        dlon = np.radians(lon2 - lon1)
        a = np.sin(dlat / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlon / 2) ** 2
        return float(2 * radius * np.arcsin(np.sqrt(np.clip(a, 0, 1))))
    distance_rows = []
    sites = site.to_dict("records")
    for i, first in enumerate(sites):
        for second in sites[i+1:]:
            distance_rows.append({
                "SiteA": first["LaunchSite"], "SiteB": second["LaunchSite"],
                "DistanceKm": round(haversine_km(first["Latitude"], first["Longitude"], second["Latitude"], second["Longitude"]), 2)
            })
    distance_df = pd.DataFrame(distance_rows, columns=["SiteA", "SiteB", "DistanceKm"])
    distance_df.to_csv(OUT_DIR / "launch_site_pairwise_distances_km.csv", index=False)
    site.to_csv(OUT_DIR / "map_launch_site_summary.csv", index=False)
    fmap.get_root().html.add_child(folium.Element(
        '<div style="position:fixed;top:10px;left:55px;z-index:9999;background:white;padding:8px 12px;border:1px solid #bbb;border-radius:5px;font-family:Arial">'
        '<b>SpaceX Launch Sites</b><br><small>Markers show CSV-derived record counts and success rates. Pairwise Haversine distances are exported to CSV.</small></div>'
    ))
    fmap.save(str(OUT_DIR / "spacex_launch_sites_map.html"))


def train_models(df: pd.DataFrame) -> pd.DataFrame:
    # Avoid directly using outcome strings or leakage-derived labels as features.
    feature_candidates = ["FlightNumber", "PayloadMass", "Orbit", "LaunchSite", "BoosterVersion",
                          "Flights", "GridFins", "Reused", "Legs", "Block", "ReusedCount"]
    features = [c for c in feature_candidates if c in df.columns]
    model_df = df.dropna(subset=["Class"]).copy()
    X, y = model_df[features].copy(), model_df["Class"].astype(int)
    if y.nunique() < 2 or len(model_df) < 25:
        raise ValueError("Insufficient rows or target classes for classification; check course dataset.")
    categorical = X.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    numeric = [c for c in X.columns if c not in categorical]
    transformers = []
    if numeric:
        transformers.append(("num", Pipeline([("imputer", SimpleImputer(strategy="median")),
                                                ("scaler", StandardScaler())]), numeric))
    if categorical:
        transformers.append(("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                                                ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical))
    preprocessor = ColumnTransformer(transformers=transformers, remainder="drop")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    estimators = {
        "Logistic Regression": LogisticRegression(max_iter=3000, class_weight="balanced"),
        "Decision Tree": DecisionTreeClassifier(random_state=42, class_weight="balanced", max_depth=4),
        "Random Forest": RandomForestClassifier(n_estimators=300, random_state=42, class_weight="balanced", min_samples_leaf=2),
        "Support Vector Machine": SVC(kernel="rbf", class_weight="balanced")
    }
    rows, fitted = [], {}
    for name, estimator in estimators.items():
        pipe = Pipeline([("preprocess", clone(preprocessor)), ("model", estimator)])
        pipe.fit(X_train, y_train)
        pred = pipe.predict(X_test)
        rows.append({"Model": name,
                     "Accuracy": accuracy_score(y_test, pred),
                     "Precision": precision_score(y_test, pred, zero_division=0),
                     "Recall": recall_score(y_test, pred, zero_division=0),
                     "F1": f1_score(y_test, pred, zero_division=0)})
        fitted[name] = pipe
    metrics = pd.DataFrame(rows).sort_values(["F1", "Accuracy"], ascending=False)
    metrics.to_csv(OUT_DIR / "model_metrics.csv", index=False)
    best_name = metrics.iloc[0]["Model"]
    best = fitted[best_name]
    y_pred = best.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    (OUT_DIR / "classification_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    fig, ax = plt.subplots(figsize=(6, 5))
    ConfusionMatrixDisplay.from_predictions(y_test, y_pred, display_labels=["Unsuccessful", "Successful"],
                                            cmap="Blues", colorbar=False, ax=ax)
    ax.set_title(f"Confusion Matrix — {best_name}")
    safe_savefig("confusion_matrix.png")
    try:
        # A lightweight interpretable parameter search for the decision tree, using training data only.
        tree_pipe = Pipeline([("preprocess", clone(preprocessor)),
                              ("model", DecisionTreeClassifier(random_state=42, class_weight="balanced"))])
        grid = GridSearchCV(tree_pipe, {"model__max_depth": [2, 3, 4, 5, None],
                                       "model__criterion": ["gini", "entropy"]},
                            cv=5, scoring="f1", n_jobs=-1)
        grid.fit(X_train, y_train)
        (OUT_DIR / "decision_tree_best_params.json").write_text(json.dumps(grid.best_params_, indent=2), encoding="utf-8")
        (OUT_DIR / "decision_tree_cv_f1.txt").write_text(f"Best 5-fold CV F1: {grid.best_score_:.4f}\n", encoding="utf-8")
    except Exception as exc:
        (OUT_DIR / "decision_tree_gridsearch_note.txt").write_text(f"Grid search not completed: {exc}\n", encoding="utf-8")
    print("\nModel metrics (hold-out test set):")
    print(metrics.to_string(index=False, formatters={c: (lambda x: f"{x:.3f}") for c in ["Accuracy", "Precision", "Recall", "F1"]}))
    print("Best model by F1:", best_name)
    return metrics


def main():
    print("Loading historical course dataset...")
    df = load_course_dataset()
    print(f"Rows: {len(df)} | Columns: {len(df.columns)} | Target distribution: {df['Class'].value_counts().to_dict()}")
    df.to_csv(OUT_DIR / "cleaned_falcon9_dataset.csv", index=False)
    missing = df.isna().sum().sort_values(ascending=False)
    missing.to_csv(OUT_DIR / "missing_values_by_column.csv", header=["missing_count"])
    make_eda(df)
    sql = run_sql(df)
    print("\nSQL summary by launch site:\n", sql["site"].to_string(index=False))
    make_map(df)
    metrics = train_models(df)
    summary = {
        "rows": int(len(df)), "columns": int(len(df.columns)),
        "landing_success_count": int((df["Class"] == 1).sum()),
        "landing_failure_count": int((df["Class"] == 0).sum()),
        "launch_sites": df["LaunchSite"].value_counts().to_dict(),
        "best_model_by_f1": str(metrics.iloc[0]["Model"]),
        "best_model_metrics": {k: float(metrics.iloc[0][k]) for k in ["Accuracy", "Precision", "Recall", "F1"]}
    }
    (OUT_DIR / "run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("\nCreated artifacts in:", OUT_DIR)
    print("Main outputs: cleaned_falcon9_dataset.csv, model_metrics.csv, confusion_matrix.png, SQL summaries, plots, and map.")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nPROJECT RUN FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
