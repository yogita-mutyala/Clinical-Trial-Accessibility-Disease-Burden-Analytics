from pathlib import Path
import pandas as pd
def load_and_standardize(path: Path, kind: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # standardize column names
    df.columns = [c.strip().lower() for c in df.columns]
    if kind == "trials":
        expected = {"state_abbr", "disease_group", "trial_count"}
        missing = expected - set(df.columns)
        if missing:
            raise ValueError(f"Trials file is missing columns: {missing}")
        df["state_abbr"] = df["state_abbr"].astype(str).str.strip().str.upper()
        df["disease_group"] = df["disease_group"].astype(str).str.strip()
        df["trial_count"] = pd.to_numeric(df["trial_count"], errors="coerce")
        df = df.dropna(subset=["state_abbr", "disease_group", "trial_count"])
        df["trial_count"] = df["trial_count"].astype(int)
        df = df.drop_duplicates(subset=["state_abbr", "disease_group"])
    elif kind == "cdi":
        expected = {"state_abbr", "state_name", "disease_group", "burden_value"}
        missing = expected - set(df.columns)
        if missing:
            raise ValueError(f"CDI file is missing columns: {missing}")
        df["state_abbr"] = df["state_abbr"].astype(str).str.strip().str.upper()
        df["state_name"] = df["state_name"].astype(str).str.strip()
        df["disease_group"] = df["disease_group"].astype(str).str.strip()
        df["burden_value"] = pd.to_numeric(df["burden_value"], errors="coerce")
        if "year_end" in df.columns:
            df["year_end"] = pd.to_numeric(df["year_end"], errors="coerce")
        if "year_start" in df.columns:
            df["year_start"] = pd.to_numeric(df["year_start"], errors="coerce")
        df = df.dropna(subset=["state_abbr", "disease_group", "burden_value"])
        df = df.drop_duplicates(subset=["state_abbr", "disease_group"])
    elif kind == "population":
        # expected columns: state_abbr, state_name, population
        expected = {"state_abbr", "state_name", "population"}
        missing = expected - set(df.columns)
        if missing:
            raise ValueError(f"Population file is missing columns: {missing}")
        df["state_abbr"] = df["state_abbr"].astype(str).str.strip().str.upper()
        df["state_name"] = df["state_name"].astype(str).str.strip()
        df["population"] = pd.to_numeric(df["population"], errors="coerce")
        df = df.dropna(subset=["state_abbr", "population"])
        df["population"] = df["population"].astype(float)
        df = df.drop_duplicates(subset=["state_abbr"])
    else:
        raise ValueError(f"Unknown kind: {kind}")
    return df
def integrate_data() -> pd.DataFrame:
    base = Path("data/processed")
    trials_path = base / "ctsccounts.csv"
    cdi_path = base / "cdi_clean.csv"
    pop_path = base / "population_clean.csv"
    trials = load_and_standardize(trials_path, "trials")
    cdi = load_and_standardize(cdi_path, "cdi")
    pop = load_and_standardize(pop_path, "population")
    # Validate key before merge
    if trials.duplicated(["state_abbr", "disease_group"]).any():
        raise ValueError("Duplicate state_abbr + disease_group rows found in trials table.")
    if cdi.duplicated(["state_abbr", "disease_group"]).any():
        raise ValueError("Duplicate state_abbr + disease_group rows found in CDI table.")
    if pop.duplicated(["state_abbr"]).any():
        raise ValueError("Duplicate state_abbr rows found in population table.")
    # Merge trials + CDI
    merged = trials.merge(
        cdi,
        on=["state_abbr", "disease_group"],
        how="inner",
        validate="one_to_one",
        suffixes=("_trial", "_cdi")
    )
    # Merge population
    merged = merged.merge(
        pop,
        on="state_abbr",
        how="left",
        validate="many_to_one",
        suffixes=("", "_pop")
    )
    # clean state_name columns
    if "state_name_trial" in merged.columns and "state_name_cdi" in merged.columns:
        merged["state_name"] = merged["state_name_trial"].fillna(merged["state_name_cdi"])
        merged = merged.drop(columns=["state_name_trial", "state_name_cdi"])
    elif "state_name" not in merged.columns:
        state_name_cols = [c for c in merged.columns if c.startswith("state_name")]
        if state_name_cols:
            merged["state_name"] = merged[state_name_cols[0]]
    # normalise
    merged["trials_per_million"] = (merged["trial_count"] / merged["population"]) * 1_000_000
    # streamline col names of burden
    merged = merged.rename(columns={
        "burden_value": "burden_value",
        "unit": "burden_unit",
        "value_type": "burden_value_type"
    })
    # keep columns together
    cols_first = [
        "state_abbr", "state_name", "disease_group",
        "trial_count", "trials_per_million",
        "burden_value", "burden_unit", "burden_value_type",
        "question", "year_start", "year_end",
        "population"
    ]
    cols_rest = [c for c in merged.columns if c not in cols_first]
    merged = merged[cols_first + cols_rest]
    # Final validation
    print("Merged rows:", len(merged))
    print("Unique state-disease pairs:", merged[["state_abbr", "disease_group"]].drop_duplicates().shape[0])
    print("Missing population rows:", merged["population"].isna().sum())
    print("Missing trial counts:", merged["trial_count"].isna().sum())
    print("Missing burden values:", merged["burden_value"].isna().sum())
    return merged
if __name__ == "__main__":
    integrated = integrate_data()
    integrated.to_csv("integrated_state_disease_dataset.csv", index=False)