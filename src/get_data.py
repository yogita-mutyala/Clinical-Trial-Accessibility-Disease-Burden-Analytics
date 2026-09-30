import argparse
import json
import sys
from pathlib import Path
import pandas as pd
import requests
# API URL
BASE_URL = "https://clinicaltrials.gov/api/v2/studies"
# Filter country
COUNTRY = "United States"
# Max limit
MAX_TRIALS = 20000
# Repo paths
BASE_DIR = Path(__file__).resolve().parents[1]   # repo/
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)
# Search conditions
CONDITIONS = [
    "breast cancer", "diabetes", "asthma", "hypertension",
    "lung cancer", "prostate cancer", "depression", "anxiety",
    "obesity", "alzheimer disease", "parkinson disease",
    "covid-19", "arthritis", "heart failure", "stroke",
]
def fetch_trials_for_conditions(conditions, country="United States", page_size=1000, max_trials=MAX_TRIALS):
    # Store data and avoid duplicates
    records = []
    seen_ids = set()
    total_count = 0
    # Session for faster requests
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    try:
        for condition in conditions:
            page_token = None
            while True:
                # Stop if we reach the limit
                if total_count >= max_trials:
                    return records
                params = {
                    "query.term": condition,
                    "query.locn": country,
                    "pageSize": page_size,
                }
                if page_token:
                    params["pageToken"] = page_token

                resp = session.get(BASE_URL, params=params, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                studies = data.get("studies", data.get("hits", []))
                for hit in studies:
                    if total_count >= max_trials:
                        return records
                    proto = hit.get("study", hit).get("protocolSection", {})
                    ident = proto.get("identificationModule", {})
                    status = proto.get("statusModule", {})
                    cond_mod = proto.get("conditionsModule", {})
                    loc_mod = proto.get("contactsLocationsModule", {})
                    nct_id = ident.get("nctId") or hit.get("id")
                    # Skip duplicate
                    if not nct_id or nct_id in seen_ids:
                        continue
                    seen_ids.add(nct_id)
                    conditions_list = cond_mod.get("conditions", []) or []
                    locations = loc_mod.get("locations", []) or []
                    records.append({
                        "search_condition": condition,
                        "nct_id": nct_id,
                        "title": ident.get("briefTitle"),
                        "conditions": "; ".join(conditions_list),
                        "recruitment_status": status.get("overallStatus"),
                        "locations_raw": json.dumps(locations),
                    })
                    total_count += 1
                page_token = data.get("nextPageToken")
                if not page_token:
                    break
        return records
    finally:
        session.close()
def save_dataset(df, output_path):
    output_path = Path(output_path)
    # Force relative outputs into repo/data/raw
    if not output_path.is_absolute():
        output_path = RAW_DIR / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Save based on file type
    if output_path.suffix.lower() == ".json":
        df.to_json(output_path, orient="records", indent=2)
    else:
        df.to_csv(output_path, index=False)
def print_dataset(df):
    # Print to terminal as CSV
    df.to_csv(sys.stdout, index=False)
def parse_args():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--scrape", type=int, metavar="N")
    group.add_argument("--save", type=str, metavar="PATH")
    return parser.parse_args()
def main():
    args = parse_args()
    # Scrape N rows and print
    if args.scrape is not None:
        n = min(args.scrape, MAX_TRIALS)
        records = fetch_trials_for_conditions(CONDITIONS, COUNTRY, max_trials=n)
        print_dataset(pd.DataFrame(records))
        return
    # Save full data
    if args.save:
        records = fetch_trials_for_conditions(CONDITIONS, COUNTRY, max_trials=MAX_TRIALS)
        df = pd.DataFrame(records)
        save_dataset(df, args.save)
        print(f"Saved {len(df)} trials")
        return
    # Default: print all
    records = fetch_trials_for_conditions(CONDITIONS, COUNTRY, max_trials=MAX_TRIALS)
    print_dataset(pd.DataFrame(records))
if __name__ == "__main__":
    main()