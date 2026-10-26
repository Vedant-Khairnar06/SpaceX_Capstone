# SpaceX Falcon 9 Data Science Capstone

## Project goal
Analyze historic Falcon 9 launch outcomes and build a classification baseline for first-stage landing success. The workflow covers SpaceX API collection, Wikipedia scraping, data wrangling, exploratory visualization, SQL, Folium, Plotly Dash, and machine-learning evaluation.

## Files
- `SpaceX_Capstone_Workflow.ipynb` — structured, section-by-section capstone notebook.
- `collect_sources.py` — SpaceX API requests and Wikipedia scraping.
- `run_analysis.py` — data validation, EDA charts, SQLite queries, Folium map, model comparison, and confusion matrix.
- `spacex_dash_app.py` — interactive dashboard with launch-site dropdown, payload slider, landing-outcome pie, and payload/outcome scatter.
- `Data Science Capstone Project Report.pdf` — report with methodology, reference findings, figures, caveats, and citations.
- `SpaceX_Capstone_Final_Presentation.pdf` — presentation PDF.
- `SpaceX_Capstone_Final_Presentation.pptx` — editable presentation slides.
- `requirements.txt` — dependencies.
- `SUBMISSION_GUIDE.md` — final upload and GitHub steps.
- `assets/` — figures used in the report/presentation.

## Historical course dataset
The analysis uses the historical course dataset with fields including `FlightNumber`, `PayloadMass`, `Orbit`, `LaunchSite`, and binary target `Class` (0 = unsuccessful landing, 1 = successful landing). If your course provides its own CSV, prefer that file and save it as `dataset_part_2_DEL.csv` in this folder. Otherwise, `run_analysis.py` attempts to download a publicly available mirror from the source repository cited below.

## Run the project
1. Use Python 3.10 or newer.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the analysis:
   ```bash
   python run_analysis.py
   ```
4. Run the dashboard in a second terminal:
   ```bash
   python spacex_dash_app.py
   ```
5. Open the local Dash URL displayed in the terminal, normally `http://127.0.0.1:8050/`.
6. In Jupyter, open `SpaceX_Capstone_Workflow.ipynb` and use **Run All** to generate notebook outputs.

The analysis writes current metrics, SQL tables, charts, the cleaned dataset, an interactive map, and a pairwise launch-site Haversine-distance table into the `outputs/` folder. It reports metrics from the selected CSV rather than hard-coding model scores.

## Important interpretation note
The report and slides show some explicitly attributed findings from a published analysis of the historical course dataset as **reference benchmarks** (including its reported 88.9% Decision Tree accuracy). They are not presented as metrics independently computed by this package. Before final submission, execute the code and update the written conclusions and screenshots with your own generated outputs. Live SpaceX API data may have a different time range and should not be mixed with the historic course dataset without stating the distinction.

## Data sources and attribution
- SpaceX API v4: https://api.spacexdata.com/v4/launches/past
- Wikipedia launch list: https://en.wikipedia.org/wiki/List_of_Falcon_9_and_Falcon_Heavy_launches
- Public historical course-data reference mirror and published benchmark findings: https://github.com/DanielEduardoLopez/IBM-SpaceX

The source repository is an external reference/data mirror, not your personal GitHub project. Create a repository under your own account and upload this package before submitting the project URL.
