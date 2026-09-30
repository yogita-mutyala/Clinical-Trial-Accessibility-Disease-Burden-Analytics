# Clinical Trial Accessibility and Disease Burden Analysis in the United States

This project investigates whether clinical trials are proportionally available in U.S. regions and disease categories where they are most needed. It integrates data from ClinicalTrials.gov, the CDC Chronic Disease Indicators dataset, and U.S. Census Bureau population data to produce a state-disease level dataset that compares trial availability against disease burden.

---

## Repository Structure

```
github_repository_structure/
├── README.md
├── requirements.txt
├── proposal.pdf
├── data/
│   ├── raw/
│   │   ├── clinical_trials_us.csv
│   │   ├── CDI_Data.csv
│   │   └── StatePopulation.csv
│   └── processed/
│       ├── ct_clean.csv
│       ├── cdi_clean.csv
│       ├── population_clean.csv
│       └── integrated_state_disease_dataset.csv
├── results/
│   ├── final_report.pdf
│   └── analyze_visualize.ipynb
└── src/
    ├── get_data.py
    ├── clean_data.py
    ├── integrate_data.py
    ├── analyze_visualize.ipynb
    └── utils/
```

---

## Requirements

### Prerequisites
- Python 3.8 or higher
- pip

### Install Dependencies

Clone the repository and install all required libraries using:

```bash
pip install -r requirements.txt
```

---

## Data Sources

The raw data files used in this project come from the following public sources:

| Dataset | Source | URL |
|---|---|---|
| ClinicalTrials.gov | National Library of Medicine API | https://clinicaltrials.gov/data-api/api |
| CDC Chronic Disease Indicators | CDC Data Portal | https://data.cdc.gov/Chronic-Disease-Indicators/U-S-Chronic-Disease-Indicators/hksd-2xuw |
| State Population | U.S. Census Bureau | https://www.census.gov/data/developers/data-sets/popest-popproj/popest.html |

---

## How to Get the Data

Run the following script to query the ClinicalTrials.gov API and download the raw data. The script saves the output to `data/raw/`.

```bash
python src/get_data.py
```

For the CDC Chronic Disease Indicators and State Population data, download the CSV files manually from the URLs listed above and place them in `data/raw/` with the following filenames:
- `CDI_Data.csv`
- `StatePopulation.csv`

---

## How to Clean the Data

Run the cleaning script to parse, filter, and standardize all three raw datasets. Cleaned files are saved to `data/processed/`.

```bash
python src/clean_data.py
```

This script handles the following for each source:
- **ClinicalTrials.gov**: Parses JSON-formatted location fields, explodes site rows, filters to U.S. locations, maps free-text conditions to disease categories, and aggregates to one trial count per state-disease pair.
- **CDC CDI**: Filters to nine disease topics, selects one representative question per disease group, and retains the most recent observation per state-disease pair.
- **Population**: Removes aggregate region rows, standardizes state names to two-letter abbreviations, and formats the population column as numeric.

---

## How to Integrate the Data

Run the integration script to merge all three cleaned datasets into a single analysis-ready table. The output is saved to `data/processed/integrated_state_disease_dataset.csv`.

```bash
python src/integrate_data.py
```

This script performs the following joins:
- Inner join between trial counts and CDI burden on `state_abbr` and `disease_group`
- Left join with population data on `state_abbr`
- Computes `trials_per_million` as a normalized access metric

The final integrated table contains 347 rows, one per fully matched state-disease pair, across 50 states and 7 disease groups.

---

## How to Run the Analysis and Produce Visualizations

Run the analysis script to generate all four visualizations and print key findings to the console.

```bash
jupyter notebook results/analyze_visualize.ipynb
```

This script produces the following outputs:

| Figure | Description |
|---|---|
| Total Clinical Trials by Disease | Horizontal bar chart showing trial counts aggregated by disease group |
| Clinical Trials per Million by State | Horizontal bar chart showing population-normalized trial availability by state |
| Disease Burden vs Trial Availability | Scatter plot comparing burden value against trials per million for each state-disease pair |
| Top Mismatches | Horizontal bar chart of the top 10 state-disease pairs ranked by mismatch score |

The mismatch score is computed by z-score normalizing both `burden_value` and `trials_per_million` and taking the difference, so that high-burden, low-trial pairs rank highest regardless of the unit of measurement used per disease.

---

## Results

The final project report is available at `results/final_report.pdf`. Key findings include:

- Cancer dominates clinical trial activity by a wide margin relative to all other disease categories.
- Smaller states rank higher than larger states in per-capita trial availability once population is accounted for.
- There is no consistent positive relationship between disease burden and trial availability across state-disease pairs.
- North Carolina, Virginia, and Arkansas show the largest cancer-related mismatches; Tennessee shows the largest cardiovascular mismatch.
