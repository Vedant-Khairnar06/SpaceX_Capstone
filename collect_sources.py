"""Demonstration of both collection methods required by the capstone: SpaceX API + web scraping."""
from pathlib import Path
from io import StringIO
import requests
import pandas as pd
from bs4 import BeautifulSoup

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(exist_ok=True)
HEADERS = {"User-Agent": "Mozilla/5.0 (educational capstone data collection)"}

# API data collection: launch list plus reference endpoints.
for endpoint, filename in [
    ("launches/past", "api_launches_raw.json"),
    ("rockets", "api_rockets.json"),
    ("launchpads", "api_launchpads.json"),
    ("payloads", "api_payloads.json"),
    ("cores", "api_cores.json"),
]:
    url = f"https://api.spacexdata.com/v4/{endpoint}"
    response = requests.get(url, timeout=30, headers=HEADERS)
    response.raise_for_status()
    (OUT / filename).write_text(response.text, encoding="utf-8")
    print(endpoint, response.status_code, "->", filename)

launches = pd.json_normalize(requests.get("https://api.spacexdata.com/v4/launches/past", timeout=30, headers=HEADERS).json())
launches.to_csv(OUT / "api_launches_normalized.csv", index=False)
print("Normalized launch dataframe:", launches.shape)

# Web scraping: inspect the current Falcon 9 launch list and preserve tables.
wiki_url = "https://en.wikipedia.org/wiki/List_of_Falcon_9_and_Falcon_Heavy_launches"
resp = requests.get(wiki_url, timeout=30, headers=HEADERS)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")
print("Wikipedia page title:", soup.title.get_text(" ", strip=True) if soup.title else "No title found")
tables = pd.read_html(StringIO(resp.text))
for idx, table in enumerate(tables):
    table.to_csv(OUT / f"wikipedia_table_{idx:02d}.csv", index=False)
print("Scraped", len(tables), "tables to", OUT)
