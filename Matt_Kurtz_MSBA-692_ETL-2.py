#!/usr/bin/env python
# coding: utf-8

# In[6]:


get_ipython().system('pip install psycopg2-binary')


# In[2]:


get_ipython().system('pip3 install dash plotly sqlalchemy pandas psycopg2-binary')


# In[26]:


import requests
import pandas as pd
import logging
from sqlalchemy import create_engine

API_KEY = "YOUR_API_KEY"

SUPABASE_CONNECTION = (
    "postgresql://postgres:YOURPASSWORD"
    "@db.ewbnlnslijasdjgjexpo.supabase.co:5432/postgres"
)

YEAR = 2025

logging.basicConfig(
    filename="etl_log.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

engine = create_engine(SUPABASE_CONNECTION)

def extract_records():
    logging.info("Extracting college football records data")

    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    url = f"https://api.collegefootballdata.com/records?year={YEAR}"

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"API request failed: {response.status_code} - {response.text}")

    logging.info("API extraction successful")

    return response.json()

def transform_data(raw_data):
    logging.info("Beginning data transformation")

    records = []

    for item in raw_data:
        team_name = item.get("team")
        conference = item.get("conference")

        total = item.get("total", {})

        wins = total.get("wins")
        losses = total.get("losses")

        records.append({
            "team_name": team_name,
            "conference": conference,
            "wins": wins,
            "losses": losses
        })

    df = pd.DataFrame(records)

    df["team_name"] = df["team_name"].astype(str).str.strip()
    df["conference"] = df["conference"].astype(str).str.strip()

    df = df[df["conference"].isin(["SEC", "Big Ten"])]

    df["wins"] = pd.to_numeric(df["wins"], errors="coerce")
    df["losses"] = pd.to_numeric(df["losses"], errors="coerce")

    df = df.dropna(subset=["team_name", "conference", "wins", "losses"])

    df["wins"] = df["wins"].astype(int)
    df["losses"] = df["losses"].astype(int)

    df["win_percentage"] = (
        df["wins"] / (df["wins"] + df["losses"])
    ).round(3)

    df["win_percentage"] = df["win_percentage"].fillna(0)

    logging.info(f"Transformation complete. Rows after filtering: {len(df)}")

    return df

def validate_data(df):
    logging.info("Running data quality checks")

    if len(df) == 0:
        raise Exception("Validation failed: No records available after transformation.")

    null_count = df.isnull().sum().sum()
    if null_count > 0:
        logging.warning(f"Null values detected: {null_count}")

    duplicate_count = df.duplicated(subset=["team_name"]).sum()
    if duplicate_count > 0:
        logging.warning(f"Duplicate team records found: {duplicate_count}")
        df = df.drop_duplicates(subset=["team_name"])

    if (df["wins"] < 0).any():
        raise Exception("Validation failed: wins contains negative values.")

    if (df["losses"] < 0).any():
        raise Exception("Validation failed: losses contains negative values.")

    if ((df["win_percentage"] < 0) | (df["win_percentage"] > 1)).any():
        raise Exception("Validation failed: win_percentage outside expected range.")

    required_columns = [
        "team_name",
        "conference",
        "wins",
        "losses",
        "win_percentage"
    ]

    for column in required_columns:
        if column not in df.columns:
            raise Exception(f"Validation failed: Missing required column {column}")

    logging.info("Data validation successful")

    return df

def remove_existing_records(df):
    logging.info("Checking existing records for incremental load")

    try:
        existing = pd.read_sql("SELECT team_name FROM teams", engine)

        df = df[
            ~df["team_name"].isin(existing["team_name"])
        ]

        logging.info(f"New records to load: {len(df)}")

    except Exception:
        logging.info("No existing teams table found. Full load will occur.")

    return df

def load_data(df):
    logging.info("Loading data into Supabase PostgreSQL")

    if len(df) == 0:
        logging.info("No new records to load.")
        print("No new records to load.")
        return

    df.to_sql(
        "teams",
        engine,
        if_exists="append",
        index=False
    )

    logging.info(f"{len(df)} rows loaded successfully")

def export_csv(df):
    file_name = "analytics_teams.csv"

    df.to_csv(file_name, index=False)

    logging.info(f"Analytics-ready CSV exported: {file_name}")

def main():
    try:
        logging.info("ETL workflow started")

        raw_data = extract_records()

        df = transform_data(raw_data)

        df = validate_data(df)

        export_csv(df)

        df = remove_existing_records(df)

        load_data(df)

        logging.info("ETL workflow completed successfully")

        print("ETL Process Completed Successfully")

    except Exception as e:
        logging.error(f"ETL Failed: {e}")
        print(f"ETL Failed: {e}")

if __name__ == "__main__":
    main()

