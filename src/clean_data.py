# process clinical trials data
import pandas as pd
# read data
ct_raw = pd.read_csv('C:\\Dashboard\\DSCI 510\\Project\\Project_Repository_Yogita_Mutyala\\data\\raw\\clinical_trials_us.csv')
# parse location_raw
import json
def parse_locations(x):
    try:
        return json.loads(x)
    except:
        return []
ct_raw['locations_parsed'] = ct_raw['locations_raw'].apply(parse_locations)
# explode locations
ct_raw_expanded = ct_raw.explode('locations_parsed')
# extract fields: city,state,facility and country
ct_raw_expanded['city'] = ct_raw_expanded['locations_parsed'].apply(lambda x: x.get('city', None) if isinstance(x, dict) else None)
ct_raw_expanded['state'] = ct_raw_expanded['locations_parsed'].apply(lambda x: x.get('state', None) if isinstance(x, dict) else None)
ct_raw_expanded['facility'] = ct_raw_expanded['locations_parsed'].apply(lambda x: x.get('facility', None) if isinstance(x, dict) else None)
ct_raw_expanded['country'] = ct_raw_expanded['locations_parsed'].apply(lambda x: x.get('country', None) if isinstance(x, dict) else None)
# keep only US locations
ct_raw_expanded = ct_raw_expanded[ct_raw_expanded['country'] == 'United States']
# clean state names (remove leading/trailing whitespace) and filter out rows with invalid characters in search_condition
ct_raw_expanded['state'] = ct_raw_expanded['state'].str.strip()
ct_raw_clean = ct_raw_expanded[~ct_raw_expanded["search_condition"].str.contains(r"[{}:\[\]\"]", regex=True, na=False)]
#diseasemapping
disease_map = {
    "diabetes": "Diabetes",
    "breast cancer": "Cancer",
    "prostate cancer": "Cancer",
    "lung cancer": "Cancer",
    "hypertension": "Cardiovascular Disease",
    "stroke": "Cardiovascular Disease",
    "heart failure": "Cardiovascular Disease",
    "heart disease": "Cardiovascular Disease",
    "alzheimer disease": "Cognitive Health and Caregiving",
    "parkinson disease": "Cognitive Health and Caregiving",
    "asthma": "Asthma",
    "depression": "Mental Health",
    "anxiety": "Mental Health",
    "arthritis": "Arthritis",
    "copd": "Chronic Obstructive Pulmonary Disease",
    "chronic obstructive pulmonary disease": "Chronic Obstructive Pulmonary Disease",
    "chronic kidney disease": "Chronic Kidney Disease",
    "obesity": "Nutrition, Physical Activity, and Weight Status",
    "covid-19": None
}
def map_disease(search_condition):
    s = str(search_condition).lower().strip()
    for key, group in disease_map.items():
        if key in s:
            return group
    return None
ct_raw_clean["disease"] = ct_raw_clean["search_condition"].apply(map_disease)
# filter groups that also appear in CDI to work together
valid_groups = {
    "Cancer",
    "Diabetes",
    "Arthritis",
    "Asthma",
    "Cardiovascular Disease",
    "Mental Health",
    "Cognitive Health and Caregiving",
    "Chronic Obstructive Pulmonary Disease",
    "Chronic Kidney Disease"
}
ct_raw_clean = ct_raw_clean[ct_raw_clean["disease"].isin(valid_groups)]
ct_clean = ct_raw_clean[['nct_id', 'disease', 'state', 'city', 'facility']]
ct_clean = ct_clean.drop_duplicates()
# format states
state_name_to_abbr = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN",
    "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
    "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI",
    "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT",
    "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
    "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
    "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR",
    "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
}
ct_clean["state_abbr"] = ct_clean["state"].map(state_name_to_abbr)
ct_clean = ct_clean.rename(columns={"disease": "disease_group"}) if "disease" in ct_clean.columns else ct_clean
ct_clean = ct_clean.dropna(subset=["state_abbr"])
ct_agg = ct_clean.groupby(["state_abbr", "disease_group"]).size().reset_index(name="trial_count")




# process CDI data
cdi_raw = pd.read_csv("C:\\Dashboard\\DSCI 510\\Project\\Project_Repository_Yogita_Mutyala\\data\\raw\\CDI_Data.csv")
cdi_raw.columns = cdi_raw.columns.str.strip()
# Keep only the CDI topics that overlap well with the trial table
valid_topics = [
    "Cancer",
    "Diabetes",
    "Arthritis",
    "Asthma",
    "Cardiovascular Disease",
    "Mental Health",
    "Cognitive Health and Caregiving",
    "Chronic Obstructive Pulmonary Disease",
    "Chronic Kidney Disease",
]
# Keep only the 50 states
state_abbrs = [
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA",
    "ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK",
    "OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"
]
cdi_raw = cdi_raw[cdi_raw["Topic"].isin(valid_topics)].copy()
cdi_raw = cdi_raw[cdi_raw["LocationAbbr"].isin(state_abbrs)].copy()
# Standardize text
for col in ["LocationAbbr", "LocationDesc", "Topic", "Question", "StratificationCategory1", "Stratification1"]:
    if col in cdi_raw.columns:
        cdi_raw[col] = cdi_raw[col].astype(str).str.strip()
# Convert numeric columns
for col in ["DataValue", "LowConfidenceLimit", "HighConfidenceLimit", "YearStart", "YearEnd"]:
    if col in cdi_raw.columns:
        cdi_raw[col] = pd.to_numeric(cdi_raw[col], errors="coerce")
# clean version of cdi data
cdi_clean = cdi_raw[[
    "LocationAbbr",
    "LocationDesc",
    "Topic",
    "Question",
    "DataValueUnit",
    "DataValueType",
    "YearStart",
    "YearEnd",
    "DataValue",
    "LowConfidenceLimit",
    "HighConfidenceLimit"
]].copy()
cdi_clean = cdi_clean.rename(columns={
    "LocationAbbr": "state_abbr",
    "LocationDesc": "state_name",
    "Topic": "disease_group",
    "Question": "question",
    "DataValueUnit": "unit",
    "DataValueType": "value_type",
    "YearStart": "year_start",
    "YearEnd": "year_end",
    "DataValue": "burden_value",
    "LowConfidenceLimit": "ci_low",
    "HighConfidenceLimit": "ci_high"
})
cdi_clean = cdi_clean.dropna(subset=["state_abbr", "state_name", "disease_group", "burden_value"])
cdi_clean = cdi_clean.drop_duplicates()
# representative question mapping
cdi_question_map = {
    "Diabetes": "Diabetes among adults",
    "Arthritis": "Arthritis among adults",
    "Asthma": "Current asthma among adults",
    "Cardiovascular Disease": "High blood pressure among adults",
    "Mental Health": "Depression among adults",
    "Cognitive Health and Caregiving": "Subjective cognitive decline among adults aged 45 years and older",
    "Chronic Obstructive Pulmonary Disease": "Chronic obstructive pulmonary disease among adults",
    "Chronic Kidney Disease": "Incidence of treated end-stage kidney disease",
    "Cancer": "Invasive cancer (all sites combined), incidence"
}
cdi_selected = cdi_clean[cdi_clean["question"].isin(cdi_question_map.values())].copy()
# If multiple rows still remain per state + disease, aggregate them
selected_questions = set(cdi_question_map.values())
cdi_selected = cdi_clean[cdi_clean["question"].isin(selected_questions)].copy()
cdi_final = (
    cdi_selected
    .sort_values(["state_abbr", "disease_group", "year_end"])
    .drop_duplicates(subset=["state_abbr", "disease_group"], keep="last")
    [["state_abbr", "state_name", "disease_group", "question", "unit", "value_type",
      "year_start", "year_end", "burden_value", "ci_low", "ci_high"]]
)


#process population table
sp_raw = pd.read_csv("C:\\Dashboard\\DSCI 510\\Project\\Project_Repository_Yogita_Mutyala\\data\\raw\\StatePopulation.csv")
#clean col names
sp_raw.columns = ["state_name","population","pop_18_plus","percent_18_plus"]
# remove non state rows
invalid_rows = ["United States", "Northeast", "Midwest", "South", "West"]
# remove leading dots
sp_raw = sp_raw[~sp_raw["state_name"].isin(invalid_rows)]
# remove leading dots
sp_raw["state_name"] = sp_raw["state_name"].str.replace(".", "", regex=False).str.strip()
# collect required cols
sp_clean = sp_raw[["state_name", "population"]]
#fomat population
sp_clean["population"] = (
    sp_clean["population"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .str.replace(" ", "", regex=False)
)
sp_clean["population"] = pd.to_numeric(sp_clean["population"], errors="coerce")
# add state abbreviuation
state_name_to_abbr = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN",
    "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
    "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI",
    "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT",
    "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
    "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
    "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR",
    "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
}
sp_clean["state_abbr"] = sp_clean["state_name"].map(state_name_to_abbr)
sp_clean = sp_clean[["state_abbr", "state_name", "population"]]
sp_clean = sp_clean.dropna()
from pathlib import Path
# create output folder
out_dir = Path("data/processed")
out_dir.mkdir(parents=True, exist_ok=True)
# save files
ct_clean.to_csv(out_dir / "ct_clean.csv", index=False)
ct_agg.to_csv(out_dir / "ctsccounts.csv", index=False)
cdi_clean.to_csv(out_dir / "cdi_clean.csv", index=False)
sp_clean.to_csv(out_dir / "population_clean.csv", index=False)