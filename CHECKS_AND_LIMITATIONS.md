# Package validation status

## Completed checks
- All Python source files pass `py_compile` syntax checks.
- The Jupyter notebook passes `nbformat` schema validation.
- Smoke-tested the charting, SQL export, Folium map + pairwise-distance export, four-model comparison, and confusion-matrix workflow against a temporary synthetic fixture. The fixture was not saved as project data and its model scores are not used in the report.
- Rendered and visually inspected the 16-page presentation PDF and 6-page report PDF. No orphaned final page remains in the report.

## Not possible to verify in this preparation environment
- Live requests to SpaceX API and external hosts failed because DNS/network access was unavailable here.
- Dash is listed in `requirements.txt` but was not installed in this environment, so the server was not launched interactively here.
- The historical CSV download, notebook Run All, real-data model metrics, and Dash screenshot must be generated on a machine with internet access or from the CSV supplied by the course.

## Why the report includes cited reference findings
The report and presentation include explicitly attributed findings from a public historical analysis of the same course dataset so that the slides contain substantive context instead of empty “insert results” placeholders. Those figures are not claimed as independently generated results. Before submission, use `outputs/model_metrics.csv` and other outputs from your actual run to update the results and conclusion.
