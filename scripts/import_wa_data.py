#!/usr/bin/env python3
"""Import World Athletics marathon data into the project database."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pandas as pd
from datetime import date
from typing import Dict

from src.data_collection.database import Database
from src.data_collection.scraper import ETHNICITY_MAP
from src.utils.time_converter import parse_time

# World Athletics 3-letter country codes → full country names
COUNTRY_CODE_TO_NAME: Dict[str, str] = {
    "KEN": "Kenya", "ETH": "Ethiopia", "ERI": "Eritrea", "UGA": "Uganda",
    "TAN": "Tanzania", "MAR": "Morocco", "ALG": "Algeria", "TUN": "Tunisia",
    "EGY": "Egypt", "RSA": "South Africa", "NGR": "Nigeria", "GHA": "Ghana",
    "CMR": "Cameroon", "CIV": "Ivory Coast", "SEN": "Senegal",
    "JAM": "Jamaica", "BAH": "Bahamas", "TTO": "Trinidad and Tobago",
    "USA": "United States", "CAN": "Canada", "MEX": "Mexico",
    "BRA": "Brazil", "ARG": "Argentina", "PER": "Peru", "CHI": "Chile",
    "COL": "Colombia", "ECU": "Ecuador", "VEN": "Venezuela", "CRC": "Costa Rica",
    "GBR": "United Kingdom", "FRA": "France", "GER": "Germany",
    "ITA": "Italy", "ESP": "Spain", "NED": "Netherlands", "BEL": "Belgium",
    "SUI": "Switzerland", "SWE": "Sweden", "NOR": "Norway", "DEN": "Denmark",
    "FIN": "Finland", "POL": "Poland", "RUS": "Russia", "POR": "Portugal",
    "GRE": "Greece", "CZE": "Czech Republic", "HUN": "Hungary", "ROU": "Romania",
    "BUL": "Bulgaria", "SRB": "Serbia", "CRO": "Croatia", "LTU": "Lithuania",
    "LAT": "Latvia", "EST": "Estonia", "UKR": "Ukraine", "BLR": "Belarus",
    "IRL": "Ireland", "AUT": "Austria", "SVK": "Slovakia", "SLO": "Slovenia",
    "TUR": "Turkey", "ISR": "Israel",
    "CHN": "China", "JPN": "Japan", "KOR": "South Korea", "PRK": "North Korea",
    "MGL": "Mongolia", "TPE": "Taiwan", "HKG": "Hong Kong",
    "IND": "India", "PAK": "Pakistan", "BAN": "Bangladesh", "SRI": "Sri Lanka",
    "NEP": "Nepal",
    "THA": "Thailand", "VIE": "Vietnam", "INA": "Indonesia",
    "PHI": "Philippines", "MAS": "Malaysia", "SIN": "Singapore",
    "QAT": "Qatar", "BRN": "Bahrain", "UAE": "United Arab Emirates",
    "KSA": "Saudi Arabia", "KUW": "Kuwait", "OMA": "Oman",
    "AUS": "Australia", "NZL": "New Zealand",
    "ZIM": "Zimbabwe", "ZAM": "Zambia",
    "MDA": "Moldova", "GEO": "Georgia", "AZE": "Azerbaijan",
    "KAZ": "Kazakhstan", "UZB": "Uzbekistan", "TKM": "Turkmenistan",
    "KGZ": "Kyrgyzstan", "TJK": "Tajikistan",
    "LUX": "Luxembourg", "MON": "Monaco",
    "PUR": "Puerto Rico", "CUB": "Cuba", "DOM": "Dominican Republic",
    "NAM": "Namibia",
}

GENDER_MAP = {"male": "M", "female": "F"}


def country_to_ethnicity(nat_code: str) -> str:
    """Map 3-letter country code to ethnicity."""
    country = COUNTRY_CODE_TO_NAME.get(nat_code, nat_code)
    return ETHNICITY_MAP.get(country, "Unknown")


def main():
    csv_path = "data/raw/world_athletics_clean.csv"
    db_path = "data/marathon.db"

    print(f"Reading {csv_path}...")
    df = pd.read_csv(csv_path, delimiter=";", low_memory=False)
    marathon = df[df["Event"] == "Marathon"].copy()
    print(f"Marathon records: {len(marathon)}")

    # Drop rows with missing key fields
    marathon = marathon.dropna(subset=["Competitor", "DOB", "Mark", "Sex"])

    # Group by athlete (Competitor + DOB)
    marathon["athlete_key"] = marathon["Competitor"].astype(str) + "_" + marathon["DOB"].astype(str)
    athletes = marathon.groupby("athlete_key").agg({
        "Competitor": "first",
        "DOB": "first",
        "Sex": "first",
        "Nat": "first",
    }).reset_index()
    print(f"Unique athletes: {len(athletes)}")

    db = Database(db_path)

    # Import athletes
    runner_map: Dict[str, int] = {}
    for _, row in athletes.iterrows():
        key = row["athlete_key"]
        name = row["Competitor"]
        birth_year = int(str(row["DOB"])[:4])
        gender = GENDER_MAP.get(row["Sex"], "M")
        nat = row["Nat"]
        ethnicity = country_to_ethnicity(nat)
        runner_id = db.insert_runner(name, gender, birth_year, ethnicity)
        runner_map[key] = runner_id
    print(f"Imported {len(runner_map)} runners.")

    # Import results
    count = 0
    for _, row in marathon.iterrows():
        key = row["athlete_key"]
        runner_id = runner_map[key]
        race_name = row["Venue"] if pd.notna(row["Venue"]) else "Unknown"
        race_date_str = row["Date"]
        try:
            race_date = date.fromisoformat(race_date_str)
        except (ValueError, TypeError):
            race_date = date(1900, 1, 1)

        time_str = row["Mark"]
        try:
            finish_seconds = parse_time(str(time_str))
        except (ValueError, AttributeError):
            continue

        db.insert_result(runner_id, race_name, race_date, finish_seconds)
        count += 1
        if count % 2000 == 0:
            print(f"  ... {count} results imported")

    print(f"Imported {count} race results.")
    print(f"Database: {db_path}")


if __name__ == "__main__":
    main()
