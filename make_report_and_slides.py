"""Build report and presentation assets using attributed historical reference findings.
The plotted benchmark values below are explicitly sourced from an existing public
analysis of the historical IBM course dataset; they are not claimed as this user's own run.
For the user's own measured outputs, execute run_analysis.py and use files under outputs/.
"""
from pathlib import Path
import math, os, subprocess, shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, FancyArrowPatch
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'
ASSETS.mkdir(exist_ok=True)
NAVY = '#17365D'
BLUE = '#2563EB'
TEAL = '#0F9D8A'
ORANGE = '#F59E0B'
RED = '#D9485F'
PURPLE = '#7C3AED'
INK = '#243B53'
MUTED = '#52606D'
PALE = '#F3F7FB'
SOURCE_URL = 'https://github.com/DanielEduardoLopez/IBM-SpaceX'

plt.rcParams.update({'font.family':'DejaVu Sans','axes.titlesize':14,'axes.labelsize':10,'xtick.labelsize':9,'ytick.labelsize':9})

def savefig(name):
    plt.tight_layout()
    plt.savefig(ASSETS/name, dpi=180, bbox_inches='tight', facecolor='white')
    plt.close()

# 1: benchmark success trend: only source-supported values, not invented intermediate observations.
fig, ax = plt.subplots(figsize=(8.4,3.7))
ax.plot([2013,2017],[0,80], marker='o', markersize=8, linewidth=3, color=BLUE)
ax.scatter([2013,2017],[0,80], s=70, color=BLUE, zorder=3)
ax.annotate('Reported: 0% in 2013', (2013,0), xytext=(2013.35,12), arrowprops={'arrowstyle':'->','color':MUTED}, fontsize=9)
ax.annotate('Reported: about 80% by 2017', (2017,80), xytext=(2014.7,93), arrowprops={'arrowstyle':'->','color':MUTED}, fontsize=9)
ax.text(2018.2,70,'Published analysis reports\nroughly 80% stability\nafter 2017', fontsize=10, color=TEAL, bbox={'boxstyle':'round,pad=.4','facecolor':'#E5F7F2','edgecolor':'#8BDCCB'})
ax.set_xlim(2012.5,2020); ax.set_ylim(-5,108); ax.set_xticks([2013,2017,2020]); ax.set_ylabel('Landing success rate (%)'); ax.set_xlabel('Year (historical course-data period)')
ax.set_title('Reported Historical Trend in Landing Success')
ax.grid(alpha=.25)
savefig('benchmark_success_trend.png')

# 2: launch site result card / donut using reported KSC LC-39A success and failure rates.
fig, ax = plt.subplots(figsize=(5.7,4.0))
vals=[76.9,23.1]; labels=['Successful missions','Unsuccessful missions']
wedges, texts, autotexts=ax.pie(vals,labels=None,autopct='%1.1f%%',startangle=90,colors=[TEAL,RED],wedgeprops={'width':.42,'edgecolor':'white','linewidth':2},pctdistance=.78,textprops={'fontsize':10})
ax.text(0,0.07,'KSC\nLC-39A',ha='center',va='center',fontsize=13,fontweight='bold',color=NAVY)
ax.legend(wedges,labels,loc='lower center',bbox_to_anchor=(.5,-.12),ncol=1,frameon=False,fontsize=9)
ax.set_title('KSC LC-39A: Reported Success Ratio')
savefig('benchmark_ksc_donut.png')

# 3: exact orbit success rates reported; note small sample sizes.
fig, ax = plt.subplots(figsize=(7.8,4.0))
orbits=['ES-L1','GEO','HEO','SSO','SO']; rates=[100,100,100,100,0]
barcolors=[TEAL,TEAL,TEAL,TEAL,RED]
bars=ax.bar(orbits,rates,color=barcolors,width=.62)
ax.set_ylim(0,115); ax.set_ylabel('Reported launch success rate (%)'); ax.set_title('Orbit Types at the Extremes in the Historical Analysis')
for b,v in zip(bars,rates): ax.text(b.get_x()+b.get_width()/2, v+3, f'{v}%', ha='center', fontweight='bold', fontsize=10)
ax.text(.98,.62,'100% outcomes came from\nsmall mission groups; do not\ninterpret as guaranteed success.',transform=ax.transAxes,ha='right',va='center',fontsize=9,color=MUTED,bbox={'boxstyle':'round,pad=.4','facecolor':'#F3F7FB','edgecolor':'#CFD8E3'})
ax.grid(axis='y',alpha=.25)
savefig('benchmark_orbit_success.png')

# 4: payload range result highlighted, no fabricated frequency or rate values.
fig, ax = plt.subplots(figsize=(8.3,2.6))
ax.set_xlim(0,7000); ax.set_ylim(-.6,.6); ax.set_yticks([])
ax.axvline(1952,color=ORANGE,linewidth=2,linestyle='--'); ax.axvline(5300,color=ORANGE,linewidth=2,linestyle='--')
ax.add_patch(Rectangle((1952,-.22),5300-1952,.44,color=TEAL,alpha=.88))
ax.text((1952+5300)/2,0,'Highest reported success range',ha='center',va='center',color='white',fontweight='bold',fontsize=10)
ax.text(1952,-.37,'1,952 kg',ha='center',va='top',color=INK,fontweight='bold')
ax.text(5300,-.37,'5,300 kg',ha='center',va='top',color=INK,fontweight='bold')
ax.set_xlabel('Payload mass (kg)'); ax.set_title('Payload Range Associated with the Highest Reported Success Rate')
ax.grid(axis='x',alpha=.22)
savefig('benchmark_payload_range.png')

# 5: launch site facts table visual
fig, ax = plt.subplots(figsize=(8.2,3.3)); ax.axis('off')
site_table = [
 ['Launch site','Published historical finding'],
 ['CCAFS SLC-40','Most frequently used launch site'],
 ['KSC LC-39A','Highest number of successful missions; 76.9% reported success ratio'],
 ['VAFB SLC-4E','Least frequently used launch site; low successful-landing count'],
]
tbl=ax.table(cellText=site_table[1:], colLabels=site_table[0], cellLoc='left', colLoc='left', colWidths=[.25,.75], loc='center')
tbl.auto_set_font_size(False); tbl.set_fontsize(9); tbl.scale(1,1.8)
for (r,c),cell in tbl.get_celld().items():
    cell.set_edgecolor('#D7E0EA')
    if r==0: cell.set_facecolor(NAVY); cell.get_text().set_color('white'); cell.get_text().set_weight('bold')
    elif r%2: cell.set_facecolor('#F3F7FB')
ax.set_title('Launch-Site Comparison from the Referenced Historical Analysis', pad=15, color=NAVY, fontweight='bold')
savefig('benchmark_launch_site_table.png')

# 6: data pipeline diagram
fig, ax = plt.subplots(figsize=(10,2.6)); ax.set_xlim(0,10); ax.set_ylim(0,2.2); ax.axis('off')
steps=[('Collect','SpaceX API +\nWikipedia'),('Wrangle','clean, join,\nencode labels'),('Explore','plots + SQL'),('Map / App','Folium + Dash'),('Predict','classification\n+ evaluation')]
xs=[.08,2.1,4.12,6.14,8.16]
for i,(title,sub) in enumerate(steps):
    rect=FancyBboxPatch((xs[i],.55),1.65,1.15,boxstyle='round,pad=.04,rounding_size=.12',facecolor=['#E8F0FE','#E6F7F3','#FFF4E5','#F0EAFE','#FCE8EC'][i],edgecolor=['#6B9BFD','#6CC7B5','#E7B15A','#A58AF3','#E58A9B'][i],linewidth=1.5)
    ax.add_patch(rect); ax.text(xs[i]+.825,1.32,title,ha='center',va='center',fontsize=10,fontweight='bold',color=NAVY); ax.text(xs[i]+.825,.89,sub,ha='center',va='center',fontsize=8,color=INK)
    if i<4: ax.add_patch(FancyArrowPatch((xs[i]+1.68,1.12),(xs[i+1]-.05,1.12),arrowstyle='-|>',mutation_scale=12,color=MUTED,linewidth=1.3))
ax.set_title('End-to-End Analytical Workflow',fontsize=14,fontweight='bold',color=NAVY,pad=8)
savefig('workflow_pipeline.png')

# 7: SQL query cards visual
fig, ax = plt.subplots(figsize=(9,4.3)); ax.axis('off')
queries=[('1  Launch-site ranking','GROUP BY LaunchSite  |  COUNT(*)  |  AVG(Class)'),('2  Orbit comparison','GROUP BY Orbit  |  COUNT(*)  |  AVG(Class)'),('3  Flight-number trend','ORDER BY FlightNumber  |  rolling success rate')]
for i,(a,b) in enumerate(queries):
    y=.78-i*.28
    ax.add_patch(FancyBboxPatch((.04,y-.1),.92,.2,boxstyle='round,pad=.01',facecolor=['#E8F0FE','#E6F7F3','#FFF4E5'][i],edgecolor='#D7E0EA'))
    ax.text(.07,y,a,ha='left',va='center',fontsize=10,fontweight='bold',color=NAVY)
    ax.text(.52,y,b,ha='left',va='center',fontsize=8.5,color=INK)
ax.set_title('SQL Questions and Analytical Purpose',fontsize=14,fontweight='bold',color=NAVY)
savefig('sql_queries_diagram.png')

# 8: ML benchmark accuracy chart
fig, ax = plt.subplots(figsize=(6.5,3.8))
b=ax.bar(['Decision Tree'],[88.9],color=BLUE,width=.45)
ax.set_ylim(0,100); ax.set_ylabel('Reported test accuracy (%)'); ax.set_title('Published Reference Benchmark: Decision Tree')
ax.bar_label(b,labels=['88.9%'],padding=4,fontweight='bold',fontsize=12)
ax.text(.5,.42,'Prior published analysis\nusing the historical course data',transform=ax.transAxes,ha='center',va='center',fontsize=9,color=MUTED)
ax.grid(axis='y',alpha=.25)
savefig('benchmark_model_accuracy.png')

# 9: confusion matrix explanatory diagram without fabricated counts
fig, ax = plt.subplots(figsize=(5.5,3.8)); ax.axis('off')
cell_colors=[['#DDEFEA','#FCE8EC'],['#FFF0D9','#E8F0FE']]
texts=[['True Negative (TN)\nCorrectly predicts no landing','False Positive (FP)\nPredicts landing; no landing'],['False Negative (FN)\nMisses a successful landing','True Positive (TP)\nCorrectly predicts landing']]
for r in range(2):
  for c in range(2):
    x=.1+c*.45; y=.1+(1-r)*.43
    ax.add_patch(FancyBboxPatch((x,y),.39,.36,boxstyle='round,pad=.015',facecolor=cell_colors[r][c],edgecolor='#CBD5E1'))
    ax.text(x+.195,y+.18,texts[r][c],ha='center',va='center',fontsize=8,color=NAVY)
ax.text(.5,.97,'Confusion matrix: interpretation guide',transform=ax.transAxes,ha='center',va='top',fontsize=12,fontweight='bold',color=NAVY)
savefig('confusion_matrix_guide.png')

# 10: dashboard preview mock layout - shows component design without fabricated KPI values.
fig = plt.figure(figsize=(10,5.5)); fig.patch.set_facecolor('#F3F7FB')
ax=fig.add_axes([0,0,1,1]); ax.axis('off')
ax.add_patch(FancyBboxPatch((.015,.84),.97,.13,boxstyle='round,pad=.008',facecolor=NAVY,edgecolor=NAVY))
ax.text(.04,.91,'SpaceX Falcon 9 Landing Analytics',color='white',fontsize=17,fontweight='bold',transform=ax.transAxes,va='center')
ax.add_patch(FancyBboxPatch((.03,.72),.43,.08,boxstyle='round,pad=.005',facecolor='white',edgecolor='#CBD5E1'))
ax.text(.05,.76,'Launch site  [ All launch sites ▾ ]',transform=ax.transAxes,fontsize=10,color=NAVY,va='center')
ax.add_patch(FancyBboxPatch((.51,.72),.45,.08,boxstyle='round,pad=.005',facecolor='white',edgecolor='#CBD5E1'))
ax.text(.53,.76,'Maximum payload mass  ━━━━━●━━  (slider)',transform=ax.transAxes,fontsize=10,color=NAVY,va='center')
for x,y,w,h,title in [(.03,.1,.44,.55,'Landing outcome pie (computed from selected data)'),(.51,.1,.45,.55,'Payload mass vs landing outcome scatter')]:
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.006',facecolor='white',edgecolor='#CBD5E1'))
    ax.text(x+.02,y+h-.05,title,transform=ax.transAxes,fontsize=10,fontweight='bold',color=NAVY,va='center')
# pie shown as a neutral chart component sample with no claims about actual proportions
pieax=fig.add_axes([.12,.22,.23,.28]); pieax.pie([1,1],startangle=90,colors=[TEAL,RED],wedgeprops={'width':.42,'edgecolor':'white'}); pieax.text(0,0,'Computed\nat runtime',ha='center',va='center',fontsize=9,color=NAVY); pieax.axis('off')
scatterax=fig.add_axes([.58,.2,.31,.31]); scatterax.set_facecolor('white'); scatterax.set_xlabel('Payload mass (kg)',fontsize=8); scatterax.set_ylabel('Landing outcome',fontsize=8); scatterax.set_yticks([0,1],['No','Yes']); scatterax.set_xlim(0,7000); scatterax.set_ylim(-.25,1.25); scatterax.grid(alpha=.2)
scatterax.text(.5,.48,'Observed records plotted\nafter selecting filters',transform=scatterax.transAxes,ha='center',va='center',fontsize=8,color=MUTED)
fig.savefig(ASSETS/'dashboard_preview.png',dpi=180,bbox_inches='tight',facecolor=fig.get_facecolor()); plt.close(fig)

# 11: source split visual
fig, ax=plt.subplots(figsize=(8,3.6)); ax.axis('off')
for i,(title,sub,url) in enumerate([
 ('SpaceX REST API','Mission JSON, rocket/site/payload/core lookups','api.spacexdata.com/v4'),
 ('Wikipedia web scrape','Launch table columns and mission outcome records','en.wikipedia.org/wiki/List_of_Falcon_9_and_Falcon_Heavy_launches'),
 ('Historical course dataset','Standardized Falcon 9 rows for reproducible modeling','github.com/DanielEduardoLopez/IBM-SpaceX')]):
    y=.72-i*.29
    ax.add_patch(FancyBboxPatch((.04,y-.08),.92,.21,boxstyle='round,pad=.015',facecolor=['#E8F0FE','#E6F7F3','#FFF4E5'][i],edgecolor='#D7E0EA'))
    ax.text(.07,y+.06,title,ha='left',va='center',fontsize=10,fontweight='bold',color=NAVY)
    ax.text(.07,y-.015,sub,ha='left',va='center',fontsize=8.5,color=INK)
    ax.text(.95,y+.06,url,ha='right',va='center',fontsize=7.5,color=BLUE)
ax.set_title('Data sources and their roles',fontsize=14,fontweight='bold',color=NAVY)
savefig('data_sources.png')

# Static coordinate view for slides. These are launch-site coordinate examples used by the
# historical course dataset; run_analysis.py builds the actual interactive Folium map from CSV.
fig, ax = plt.subplots(figsize=(7.8,4.3))
launch_sites = [
    ('CCAFS SLC-40', -80.577366, 28.561857, BLUE),
    ('KSC LC-39A', -80.603956, 28.608058, TEAL),
    ('VAFB SLC-4E', -120.610829, 34.632093, ORANGE),
]
for label, lon, lat, color in launch_sites:
    ax.scatter(lon, lat, s=130, color=color, edgecolor='white', linewidth=1.5, zorder=3)
    offset = (4, 9) if 'VAFB' in label else (4, -15 if 'KSC' in label else 7)
    ax.annotate(label, (lon, lat), xytext=offset, textcoords='offset points', fontsize=9, fontweight='bold', color=NAVY)
ax.set_xlabel('Longitude (degrees)'); ax.set_ylabel('Latitude (degrees)')
ax.set_title('Launch Site Coordinate View (Static Overview)')
ax.set_xlim(-128,-72); ax.set_ylim(24,40); ax.grid(alpha=.22)
ax.text(.02,.02,'Coordinate view only; interactive Folium markers and counts are generated from the CSV.', transform=ax.transAxes, fontsize=8, color=MUTED)
savefig('launch_site_locations.png')

# 12: source-based findings table
source_findings = [
 ('Launch site', 'CCAFS SLC-40 was reported as the most frequently used; VAFB SLC-4E the least used.'),
 ('Success by site', 'KSC LC-39A was reported with the highest successful mission count and 76.9% success ratio.'),
 ('Orbit outcome', 'ES-L1, GEO, HEO and SSO were reported at 100%; SO at 0%, with very small samples for some orbits.'),
 ('Payload', 'The range 1,952–5,300 kg was reported as the highest-success payload range.'),
 ('Trend', 'The historical analysis reported success rising to about 80% by 2017 and stabilizing near that level.'),
 ('Model', 'A tuned Decision Tree was reported at 88.9% accuracy; it performed better on successful than unsuccessful landings.'),
]

# Presentation content: meaningful slide text + visuals; source data is explicitly attributed.
slides = [
 {'title':'SpaceX Falcon 9 Data Science Capstone','tag':'CAPSTONE PROJECT • HISTORICAL LAUNCH ANALYSIS','subtitle':'Exploring launch outcomes and predicting first-stage landing success','body':['Research question: Can historical launch, payload, orbit, launch-site and booster features help predict first-stage landing success?','Workflow: API collection • web scraping • wrangling • EDA • SQL • Folium • Dash • classification','Historical course dataset reference period: 2010–2020 in the published baseline study.'], 'img':'workflow_pipeline.png','note':'Data sources and benchmark findings are attributed in the References slide. Current outputs are regenerated by the included code.'},
 {'title':'Executive Summary','body':['The project combines two collection pathways (SpaceX API and launch-list web scraping) with a stable historical course dataset for reproducible evaluation.','Published reference analysis found launch-site, payload-mass and orbit differences; it reported improving landing success over time.','A prior analysis of this historical dataset reported a tuned Decision Tree accuracy of 88.9%. This is a reference benchmark, not a metric generated in this environment.','The supplied pipeline regenerates the cleaned dataset, figures, SQL tables, Folium map, model metrics and confusion matrix when run.'],'img':'benchmark_model_accuracy.png','note':'Reference: Daniel Eduardo López, IBM-SpaceX capstone repository (2022). Recompute metrics on your own run before submission.'},
 {'title':'Introduction and Problem Statement','body':['Falcon 9 first-stage reuse is an important operational lever because successful recovery can enable refurbishment and reuse.','Business question: Which historical mission features are associated with landing outcome, and how well can a classifier estimate landing success?','Target: `Class` (0 = unsuccessful landing; 1 = successful landing) in the historical course dataset.','Scope: descriptive analysis and prediction; associations do not establish that a feature causes a landing outcome.'],'img':'data_sources.png','note':'Historical business context and research question follow the public capstone description; cited benchmark period ends in 2020.'},
 {'title':'Data Collection — SpaceX API','body':['Send GET request to `/v4/launches/past` and normalize JSON with `pandas.json_normalize`.','Enrich launch IDs through `/rockets`, `/launchpads`, `/payloads` and `/cores` endpoints.','Extract launch date, rocket/booster, payload mass and orbit, launch-site coordinates, recovery attempt and landing result where available.','Quality controls: check HTTP status, handle missing fields and save the raw/normalized files for traceability.'],'img':'workflow_pipeline.png','note':'API endpoint: https://api.spacexdata.com/v4/launches/past'},
 {'title':'Data Collection — Web Scraping','body':['Request the Wikipedia List of Falcon 9 and Falcon Heavy launches page using `requests`.','Create a BeautifulSoup object, inspect `soup.title`, identify the launch table and parse it with `pandas.read_html`.','Save the extracted table as a versioned CSV for inspection and compare schema changes before reuse.','Web tables can change; the code checks status and records the table list rather than assuming a fixed table index.'],'img':'data_sources.png','note':'Source: https://en.wikipedia.org/wiki/List_of_Falcon_9_and_Falcon_Heavy_launches'},
 {'title':'Data Wrangling Methodology','body':['Filter to Falcon 9 records for a consistent scope; standardize field names and types.','Parse dates and create numeric model inputs; inspect missing values and duplicates before treatment.','Impute missing predictor values inside a scikit-learn preprocessing pipeline.','One-hot encode categorical fields and scale numeric values where appropriate. Split train/test data with stratification; keep preprocessing within the training pipeline to limit leakage.'],'img':'workflow_pipeline.png','note':'The raw collector, historical-data loader, and model code are included in the ZIP.'},
 {'title':'EDA with Data Visualization','body':['Launch-site bar chart: compares sample size by site; it does not alone measure operational quality.','Landing-outcome pie chart: visualizes target imbalance and explains why accuracy should not be the only metric.','Payload scatter/strip plot: examines the distribution of payload mass across landing classes.','Rolling success trend and orbit counts reveal temporal and mission-type patterns. The included code regenerates all figures from the loaded dataset.'],'img':'benchmark_success_trend.png','note':'The trend shown is the attributed published benchmark; use generated outputs/ figures for your own run.'},
 {'title':'EDA with SQL','body':['Load the cleaned launch-level data into SQLite so analysis is reproducible and queryable.','Query 1: `GROUP BY LaunchSite` for record count and mean landing class.','Query 2: `GROUP BY Orbit` for frequency and observed success rate; include counts so small groups are not overinterpreted.','Query 3: order launches by flight number to examine trend changes. The script exports each SQL result as a CSV.'],'img':'sql_queries_diagram.png','note':'Generated files: sql_launch_site_summary.csv, sql_orbit_summary.csv, sql_flight_summary.csv.'},
 {'title':'EDA Result — Launch-Site Comparison','body':['Published baseline: CCAFS SLC-40 was the most frequently used launch site.','VAFB SLC-4E was reported as the least used site, with comparatively few successful landings.','KSC LC-39A was reported to have the highest count of successful missions and a 76.9% success ratio.','Key insight: launch volume and success ratio answer different questions; do not infer the best site from count alone.'],'img':'benchmark_launch_site_table.png','note':'All findings on this slide are reference findings from the published historical course-data analysis, not current SpaceX operational statistics.'},
 {'title':'EDA Result — Success Trend over Time','body':['The referenced study reported that landing success improved over the historical flight sequence.','Its summary described success rising from 0% in 2013 to about 80% by 2017, then staying near 80%.','The chart deliberately plots only the explicitly reported year/value points; the later plateau is described as a textual finding rather than inventing annual observations.','The code computes a rolling success rate directly from the selected CSV for an updated result.'],'img':'benchmark_success_trend.png','note':'Reference values: published IBM-SpaceX capstone analysis, not an independently re-run analysis.'},
 {'title':'EDA Result — Payload and Orbit','body':['Reported high-success payload range: 1,952–5,300 kg. This is an observed range, not a causal threshold or guarantee.','The reference analysis reported 100% observed success for ES-L1, GEO, HEO and SSO; the SO category was reported at 0%.','The same analysis cautioned implicitly through small counts that 100% categories can be based on very few missions.','The included code plots actual orbit counts and success rates with denominators, so small-sample effects can be assessed.'],'img':'benchmark_orbit_success.png','note':'Use per-orbit counts alongside percentages when discussing uncertainty.'},
 {'title':'SQL Results — What the Tables Tell Us','body':['The historical reference analysis ranked CCAFS SLC-40 highest for launch usage and VAFB SLC-4E lowest.','KSC LC-39A appeared as the site with the highest success count and 76.9% reported success ratio.','Orbit summaries highlighted a mix of high observed success in a few low-frequency orbits and frequent mission types such as LEO, ISS, PO, GTO and VLEO.','The run script exports the actual grouped SQL outputs from the course dataset so these observations can be checked quantitatively.'],'img':'benchmark_launch_site_table.png','note':'SQL result CSVs are written beneath `outputs/` after execution.'},
 {'title':'Interactive Visual Analytics — Folium','body':['The map uses site latitude/longitude from the dataset and puts one marker at each launch-site location.','Marker popups show launch record count and observed landing success percentage.','The script exports pairwise Haversine distances between launch-site coordinates for a reproducible proximity comparison. A published historical analysis reported KSC LC-39A at about 6.46 km from the Atlantic Sea and 72.21 km from Orlando; such distances depend on the chosen reference point.','Run `python run_analysis.py` to create `outputs/spacex_launch_sites_map.html` and the pairwise distance CSV.'],'img':'launch_site_locations.png','note':'Actual interactive coordinate-based map is generated from the input CSV; this static view is only an overview.'},
 {'title':'Interactive Visual Analytics — Plotly Dash','body':['The provided Dash app includes a launch-site dropdown and payload-mass slider.','The pie chart dynamically summarizes successful versus unsuccessful landing outcomes for the selected site.','The scatter plot maps observed payload mass against landing class and colors points by booster version or site.','Run `python spacex_dash_app.py`, then open `http://127.0.0.1:8050/`. The slide image is a UI preview; live chart values come from the dataset.'],'img':'dashboard_preview.png','note':'Dashboard source file: spacex_dash_app.py. Use live screenshot from your own app if the course explicitly requires screenshots.'},
 {'title':'Predictive Analysis — Classification and Results','body':['Target: first-stage landing class. Candidate features include flight number, payload mass, orbit, site, booster version, reuse, grid fins, legs and block.','Models compared by code: Logistic Regression, Decision Tree, Random Forest and Support Vector Machine.','Published reference benchmark: a tuned Decision Tree reported 88.9% accuracy and performed better on successful than unsuccessful landings.','Your code calculates current accuracy, precision, recall and F1 on a held-out test split; it saves a numeric confusion matrix and tuned tree parameters.'],'img':'benchmark_model_accuracy.png','note':'Do not report the 88.9% as your own run result unless your run reproduces it. Use outputs/model_metrics.csv.'},
 {'title':'Conclusion, Limitations and Innovative Insight','body':['Historical reference findings suggest landing success improved over the studied flight sequence and reached roughly 80% by 2017.','Launch volume and success ratio should be analyzed separately: the busiest site was not the site reported with the highest success ratio.','Orbit success percentages based on small samples can look perfect without being reliable; always display counts with rates.','Limitations: historical cutoff, missing labels, class imbalance, changing operations and dataset-source drift. Re-run the pipeline and replace benchmarks with your measured outputs before final submission.'],'img':'benchmark_payload_range.png','note':'References: SpaceX API v4; Wikipedia launch list; Daniel Eduardo López, IBM-SpaceX capstone repository.'},
]

# Build deck with balanced styling and substantial text / visuals.
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

def add_text(slide, x,y,w,h,text,size=16,color=INK,bold=False,font='Aptos',align=None):
    box=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
    tf=box.text_frame; tf.clear(); tf.word_wrap=True
    p=tf.paragraphs[0]; p.text=text; p.font.name=font; p.font.size=Pt(size); p.font.bold=bold; p.font.color.rgb=RGBColor.from_string(color.lstrip('#'))
    if align is not None: p.alignment=align
    return box

def add_base(slide, index, title, tag=None):
    slide.background.fill.solid(); slide.background.fill.fore_color.rgb=RGBColor(243,247,251)
    band=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,0,0,prs.slide_width,Inches(1.0)); band.fill.solid(); band.fill.fore_color.rgb=RGBColor(23,54,93); band.line.fill.background()
    add_text(slide,.48,.16,12.3,.55,title,24,'#FFFFFF',True)
    # thin accent stripe
    stripe=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(.48),Inches(1.12),Inches(.65),Inches(.06)); stripe.fill.solid(); stripe.fill.fore_color.rgb=RGBColor(37,99,235); stripe.line.fill.background()
    footer=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,0,Inches(7.21),prs.slide_width,Inches(.29)); footer.fill.solid(); footer.fill.fore_color.rgb=RGBColor(232,239,247); footer.line.fill.background()
    add_text(slide,.48,7.245,10.7,.18,'SpaceX Falcon 9 Capstone  •  Historical course-data analysis',8,'#52606D')
    add_text(slide,12.1,7.245,.65,.18,f'{index:02d}/{len(slides):02d}',8,'#52606D',False,align=PP_ALIGN.RIGHT)

for ix, s in enumerate(slides,1):
    slide=prs.slides.add_slide(prs.slide_layouts[6]); add_base(slide,ix,s['title'],s.get('tag'))
    if ix==1:
        add_text(slide,.65,1.48,6.1,.4,s.get('tag','SPACE DATA • ANALYTICS • MACHINE LEARNING'),10,'#2563EB',True)
        add_text(slide,.65,2.0,6.0,1.35,'Exploring launch outcomes and predicting first-stage landing success',27,'#17365D',True)
        yy=3.48
        for b in s['body']:
            add_text(slide,.82,yy,5.8,.52,'• '+b,13,'#243B53'); yy+=.75
        slide.shapes.add_picture(str(ASSETS/s['img']), Inches(6.75), Inches(1.62), width=Inches(5.95))
        add_text(slide,.67,6.25,11.9,.5,s['note'],9,'#52606D')
    else:
        # Left explanatory column
        bullet_top=1.38; max_y=6.25; avail=max_y-bullet_top
        fs=14 if len(s['body'])<=4 else 12
        per=avail/len(s['body'])
        y=bullet_top
        for b in s['body']:
            # draw bullet dot
            circ=slide.shapes.add_shape(MSO_SHAPE.OVAL,Inches(.63),Inches(y+.08),Inches(.10),Inches(.10)); circ.fill.solid(); circ.fill.fore_color.rgb=RGBColor(37,99,235); circ.line.fill.background()
            tb=add_text(slide,.86,y,5.28,per-.08,b,fs,'#243B53')
            y+=per
        # Right panel
        panel=slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.38), Inches(1.36), Inches(6.45), Inches(4.98))
        panel.fill.solid(); panel.fill.fore_color.rgb=RGBColor(255,255,255); panel.line.color.rgb=RGBColor(215,224,234)
        if s.get('img'):
            slide.shapes.add_picture(str(ASSETS/s['img']), Inches(6.58), Inches(1.64), width=Inches(6.05), height=Inches(4.28))
        add_text(slide,.65,6.43,12.0,.52,s['note'],8,'#52606D')

pptx_path = ROOT/'SpaceX_Capstone_Final_Presentation.pptx'
prs.save(pptx_path)

# Export with LibreOffice to PDF and verify PDF creation.
try:
    subprocess.run(['libreoffice','--headless','--convert-to','pdf','--outdir',str(ROOT),str(pptx_path)],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
    generated_pdf = ROOT/(pptx_path.stem+'.pdf')
except Exception as exc:
    print('PowerPoint PDF conversion issue:', exc)
    generated_pdf = None

# Build longer report PDF with charts, explanations, findings, methodology and sources.
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='CoverCap', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=24, leading=30, alignment=1, textColor=colors.HexColor(NAVY), spaceAfter=16))
styles.add(ParagraphStyle(name='SubCap', parent=styles['Normal'], fontSize=12, leading=17, alignment=1, textColor=colors.HexColor(MUTED), spaceAfter=10))
styles.add(ParagraphStyle(name='HeadCap', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor(NAVY), spaceBefore=8, spaceAfter=8))
styles.add(ParagraphStyle(name='BodyCap', parent=styles['BodyText'], fontSize=9.3, leading=13.3, spaceAfter=6))
styles.add(ParagraphStyle(name='SmallCap', parent=styles['BodyText'], fontSize=7.6, leading=10, textColor=colors.HexColor(MUTED), spaceAfter=5))
report_path=ROOT/'Data Science Capstone Project Report.pdf'
doc=SimpleDocTemplate(str(report_path),pagesize=A4,rightMargin=1.7*cm,leftMargin=1.7*cm,topMargin=1.5*cm,bottomMargin=1.5*cm)
story=[Spacer(1,3.2*cm),Paragraph('DATA SCIENCE CAPSTONE PROJECT REPORT',styles['CoverCap']),Paragraph('SpaceX Falcon 9 launch analysis and first-stage landing prediction',styles['SubCap']),Spacer(1,1.0*cm),Paragraph('<b>Project scope</b>',styles['HeadCap']),Paragraph('A reproducible end-to-end workflow for public launch-data collection, wrangling, exploratory analysis, SQL summaries, geospatial visualization, an interactive dashboard, and binary classification.',styles['BodyCap']),Spacer(1,.5*cm),Paragraph('<b>Data sources</b>: SpaceX API v4, Wikipedia launch table, and a public historical IBM course-data mirror.',styles['BodyCap']),Paragraph('<b>Important results note:</b> The numerical findings in this report are explicitly attributed published reference findings from a historical course-data analysis. They are not represented as results personally generated by this report builder. Run the included analysis code and replace these reference findings with your own generated outputs before final submission.',styles['BodyCap']),PageBreak()]
sections=[
('1. Executive Summary', 'The capstone investigates whether historical launch characteristics contain useful signal about Falcon 9 first-stage landing success. It combines API-based data collection, web scraping, pandas-based wrangling, exploratory plots, SQL analysis, Folium mapping, Plotly Dash visualization, and supervised classification. A public historical analysis reported that launch success improved over time, that site/orbit/payload groups differed in observed outcomes, and that a tuned Decision Tree achieved 88.9% accuracy. These are reference findings, not live/current launch statistics. The supplied code recomputes data summaries and model evaluation from the historical course dataset.'),
('2. Introduction and Business Problem', 'Falcon 9 reuse creates an operational incentive to understand successful first-stage recovery. The analysis question is: can mission attributes such as flight number, payload mass, orbit, launch site, booster version and reuse indicators help estimate whether the first stage lands successfully? The project uses a binary label, Class = 0 for an unsuccessful landing and Class = 1 for a successful landing in the historical course dataset. This is a prediction and descriptive-analysis exercise; the observed associations should not be interpreted as causal relationships.'),
('3. Data Collection — SpaceX API', 'The collector sends GET requests to the SpaceX API v4 launch endpoint and uses `pandas.json_normalize` to flatten nested launch JSON into tabular form. Additional endpoints for rockets, launchpads, payloads and cores provide lookup information for identifier fields. The code checks HTTP status and writes raw JSON and normalized CSV artifacts to the outputs folder. API endpoint: https://api.spacexdata.com/v4/launches/past.'),
('4. Data Collection — Web Scraping', 'The web scraper requests Wikipedia’s List of Falcon 9 and Falcon Heavy launches page, parses the HTML with BeautifulSoup, records the page title, and inspects the tables available to pandas.read_html. Tables are saved to CSV for inspection. Because page structure changes over time, the scrape step prints table indices and column names rather than relying on a permanently fixed index. Source: https://en.wikipedia.org/wiki/List_of_Falcon_9_and_Falcon_Heavy_launches.'),
('5. Data Wrangling Methodology', 'The historical analysis data is standardized to predictable column names and data types. Rows lacking the essential launch identifier, site, or target are excluded; missing predictor values are handled inside a scikit-learn pipeline. Numeric features are imputed and scaled; categorical inputs are imputed and one-hot encoded. A stratified hold-out split is used, with preprocessing fitted inside the pipeline to reduce data leakage. Missingness and class balance are exported for review.'),
('6. EDA with Data Visualization', 'The workflow provides a bar chart of launch records by site, a landing-outcome distribution, a payload-mass versus outcome plot, a rolling success-rate trend by flight number, orbit-frequency plots, and missing-value summaries when appropriate. Each plot answers a distinct question: where observations are concentrated, how balanced the target is, whether payload mass distributions differ by label, how success changes over flight sequence, and how common different orbit types are. The charts should be regenerated and interpreted from your own run.'),
('7. EDA with SQL', 'The cleaned dataframe is loaded into SQLite. SQL queries group by LaunchSite to count records and calculate average Class as an observed success percentage; group by Orbit to compare volume and success; and order records by FlightNumber to inspect sequence-related patterns. Counts should always accompany percentages because a small orbit category can show a 100% observed success rate without strong evidence of a high underlying success probability. CSV outputs are saved in outputs/.'),
('8. Historical Reference Findings', 'A public historical capstone analysis of the course dataset reported CCAFS SLC-40 as the most frequently used launch site and VAFB SLC-4E as the least used. It reported KSC LC-39A as having the highest number of successful missions and a 76.9% success ratio. It also reported a payload range of 1,952–5,300 kg as the range with the highest success rate. These findings are useful as a comparison benchmark, but they can differ by data version and sampling choices.'),
('9. Orbit and Temporal Findings', 'The reference analysis reported 100% observed success for ES-L1, GEO, HEO and SSO missions, and 0% for SO. Some categories had few observations, making percentages unstable. The reference summary also reported that landing success improved from 0% in 2013 to approximately 80% by 2017, remaining around that level thereafter. The included code calculates actual counts, success rates and a rolling trend from the selected CSV rather than hard-coding those values.'),
('10. Interactive Visual Analytics — Folium and Dash', 'The Folium map plots launch sites using latitude and longitude, with circle-marker size and popup details derived from the dataset. The script also exports pairwise Haversine distances between launch sites. A prior historical analysis reported KSC LC-39A at about 6.46 km from the Atlantic Sea and 72.21 km from Orlando, FL; such estimates depend on chosen reference points. The Dash application provides a launch-site dropdown and a payload-mass slider. Its pie chart dynamically summarizes successful and unsuccessful outcomes, while its scatter plot displays observed payload mass against landing class. Run `python spacex_dash_app.py` and open http://127.0.0.1:8050/. The static preview in the slide deck demonstrates layout only; the live application computes the actual figures from the CSV.'),
('11. Predictive Analysis', 'The modeling script compares Logistic Regression, Decision Tree, Random Forest and Support Vector Machine classifiers. It uses the landing class as the target and historical mission characteristics as predictors. Accuracy, precision, recall and F1 are reported on a stratified hold-out test set. The model selected by F1 produces a numeric confusion matrix; a small GridSearchCV tunes Decision Tree depth and splitting criterion using training data only. For imbalanced outcomes, accuracy alone is not sufficient: precision, recall, F1 and both types of errors should be considered.'),
('12. Reference Model Benchmark', 'A published historical reference analysis reported 88.9% test accuracy for a tuned Decision Tree and noted better performance predicting successful landings than unsuccessful ones, leaving room to reduce false positives and false negatives. This value is included only as a cited reference benchmark. Use `outputs/model_metrics.csv`, `outputs/confusion_matrix.png` and `outputs/decision_tree_best_params.json` for the measurements produced by your own execution.'),
('13. Limitations and Risks', 'The historical dataset represents a finite time window and does not necessarily reflect current SpaceX operations. Public APIs and Wikipedia tables can change, fields can be missing, landing labels may be unknown, and the target distribution may be imbalanced. Low-frequency categories can create extreme observed percentages. The modeling split is a baseline evaluation; a time-based split may be preferable when predicting future launches. The project should not be used as an operational safety system.'),
('14. Conclusion and Next Steps', 'The project demonstrates the full data-science workflow from collection and cleaning through visualization, SQL, mapping, dashboard design and classification. A key analytical insight is that launch volume differs from landing success ratio, and success percentages must be contextualized by sample size. To finalize the submission, execute the included scripts, use the generated charts and metrics, add the actual GitHub repository URL after publishing the files, and update the conclusion with your run’s measured results.'),
]
for title, body in sections:
    story.append(Paragraph(title,styles['HeadCap']))
    story.append(Paragraph(body.replace('&','&amp;'),styles['BodyCap']))
    if title.startswith('6.'):
        story += [Image(str(ASSETS/'benchmark_success_trend.png'),width=15.8*cm,height=7.0*cm),Paragraph('Figure: documented historical trend points and textual plateau finding; source benchmark is attributed below.',styles['SmallCap'])]
    elif title.startswith('8.'):
        story += [Image(str(ASSETS/'benchmark_launch_site_table.png'),width=15.8*cm,height=6.2*cm),Image(str(ASSETS/'benchmark_ksc_donut.png'),width=10.5*cm,height=6.5*cm),Paragraph('Figures reproduce only findings stated in the cited public historical analysis.',styles['SmallCap'])]
    elif title.startswith('9.'):
        story += [Image(str(ASSETS/'benchmark_orbit_success.png'),width=15.8*cm,height=7.2*cm),Image(str(ASSETS/'benchmark_payload_range.png'),width=15.8*cm,height=4.5*cm)]
    elif title.startswith('10.'):
        story += [Image(str(ASSETS/'dashboard_preview.png'),width=16*cm,height=8.8*cm),Paragraph('Dashboard preview is a schematic UI preview; live graph values are calculated by spacex_dash_app.py.',styles['SmallCap'])]
    elif title.startswith('11.'):
        story += [Image(str(ASSETS/'workflow_pipeline.png'),width=16*cm,height=4.3*cm)]
    elif title.startswith('12.'):
        story += [Image(str(ASSETS/'benchmark_model_accuracy.png'),width=12*cm,height=7*cm),Image(str(ASSETS/'confusion_matrix_guide.png'),width=10*cm,height=6*cm)]
    story.append(Spacer(1,.15*cm))
story.append(Paragraph('References',styles['HeadCap']))
refs=[
'1. López, Daniel Eduardo. “IBM SpaceX: Applied Data Science Capstone Project.” Public repository and reported historical analysis, 28 July 2022. '+SOURCE_URL,
'2. SpaceX API v4, past launches endpoint: https://api.spacexdata.com/v4/launches/past',
'3. Wikipedia contributors. “List of Falcon 9 and Falcon Heavy launches.” https://en.wikipedia.org/wiki/List_of_Falcon_9_and_Falcon_Heavy_launches',
'4. Scikit-learn documentation: https://scikit-learn.org/stable/ (pipelines, preprocessing, model selection, classification metrics).',
'5. Folium documentation: https://python-visualization.github.io/folium/ ; Plotly Dash documentation: https://dash.plotly.com/.'
]
for r in refs: story.append(Paragraph(r.replace('&','&amp;'),styles['SmallCap']))

def page_footer(canvas, doc):
    canvas.saveState(); canvas.setFont('Helvetica',7.5); canvas.setFillColor(colors.HexColor(MUTED)); canvas.drawString(1.7*cm,.75*cm,'SpaceX Falcon 9 Capstone • historical benchmark references are attributed'); canvas.drawRightString(A4[0]-1.7*cm,.75*cm,f'Page {doc.page}'); canvas.restoreState()
doc.build(story,onFirstPage=page_footer,onLaterPages=page_footer)
print('Created deck:',pptx_path)
print('Created report:',report_path)
print('PDF deck:', generated_pdf)
