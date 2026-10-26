# Submission checklist

## 1. Run the analysis before submitting
- Put the course's historical CSV in this folder as `dataset_part_2_DEL.csv` if you have it.
- Run `pip install -r requirements.txt`.
- Run `python run_analysis.py` and review `outputs/model_metrics.csv`, `outputs/confusion_matrix.png`, the SQL CSVs, chart PNGs, `outputs/spacex_launch_sites_map.html`, and `outputs/launch_site_pairwise_distances_km.csv`.
- Open `SpaceX_Capstone_Workflow.ipynb`, use **Run All**, and save with cell outputs.
- Run `python spacex_dash_app.py`; try the launch-site dropdown and payload slider; capture your own dashboard screenshot if required.

## 2. Publish the actual project to GitHub
I cannot create a repository inside your account from this chat. To get a real project URL:
1. Sign in at https://github.com/ and create a **Public** repository named `spacex-falcon9-capstone`.
2. Upload this folder's files (including the notebook, Python files, README and requirements). Do not upload `.venv`, temporary cache files, or secrets.
3. Copy the URL of that repository. Use that real URL in the presentation/report where the rubric asks for the project's GitHub URL.

If using Git from a terminal after creating the empty GitHub repository:
```bash
git init
git add README.md requirements.txt collect_sources.py run_analysis.py spacex_dash_app.py SpaceX_Capstone_Workflow.ipynb
# Add the report, presentation, and assets after reviewing/updating them
git add .
git commit -m "Complete SpaceX Falcon 9 data science capstone"
git branch -M main
git remote add origin https://github.com/<your-username>/spacex-falcon9-capstone.git
git push -u origin main
```
Replace `<your-username>` with your GitHub username. The URL is only real after the repository is created.

## 3. Submit the right PDFs
- `Data Science Capstone Project Report.pdf` for the report upload.
- `SpaceX_Capstone_Final_Presentation.pdf` for the completed presentation PDF upload.
- The actual repository URL for the GitHub URL item.

## Accuracy reminder
This package has been syntax-checked and the analysis pipeline smoke-tested with a temporary test fixture. The execution environment used to prepare the package could not resolve external API hosts, and Dash was not installed here, so the live data download and dashboard server have not been run in this environment. Run them on your machine and replace reference findings with the actual results before submission.
