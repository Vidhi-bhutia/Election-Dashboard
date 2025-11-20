from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DATA = BASE_DIR / "All_States_GE.csv"
DB_PATH = BASE_DIR / "data" / "elections.db"

COLUMN_MAP: Dict[str, str] = {
    "State_Name": "state_name",
    "Assembly_No": "assembly_no",
    "Constituency_No": "constituency_no",
    "Year": "year",
    "month": "month",
    "Poll_No": "poll_no",
    "DelimID": "delim_id",
    "Position": "position",
    "Candidate": "candidate_name",
    "Sex": "gender",
    "Party": "party",
    "Votes": "votes",
    "Candidate_Type": "candidate_type",
    "Valid_Votes": "valid_votes",
    "Electors": "electors",
    "Constituency_Name": "constituency_name",
    "Constituency_Type": "constituency_type",
    "Sub_Region": "sub_region",
    "N_Cand": "num_candidates",
    "Turnout_Percentage": "turnout_pct",
    "Vote_Share_Percentage": "vote_share_pct",
    "Deposit_Lost": "deposit_lost",
    "Margin": "margin",
    "Margin_Percentage": "margin_pct",
    "ENOP": "enop",
    "pid": "candidate_id",
    "Party_Type_TCPD": "party_type",
    "Party_ID": "party_id",
    "last_poll": "last_poll",
    "Contested": "contested",
    "Last_Party": "last_party",
    "Last_Party_ID": "last_party_id",
    "Last_Constituency_Name": "last_constituency_name",
    "Same_Constituency": "same_constituency",
    "Same_Party": "same_party",
    "No_Terms": "num_terms",
    "Turncoat": "turncoat",
    "Incumbent": "incumbent",
    "Recontest": "recontest",
    "MyNeta_education": "education",
    "TCPD_Prof_Main": "profession_main",
    "TCPD_Prof_Main_Desc": "profession_main_desc",
    "TCPD_Prof_Second": "profession_secondary",
    "TCPD_Prof_Second_Desc": "profession_secondary_desc",
    "Election_Type": "election_type",
}

NUMERIC_COLS = {
    "assembly_no",
    "constituency_no",
    "year",
    "month",
    "poll_no",
    "delim_id",
    "position",
    "votes",
    "valid_votes",
    "electors",
    "num_candidates",
    "turnout_pct",
    "vote_share_pct",
    "margin",
    "margin_pct",
    "num_terms",
    "enop",
}

BOOL_COLS = {
    "last_poll",
    "contested",
    "same_constituency",
    "same_party",
    "turncoat",
    "incumbent",
    "recontest",
}


def _load_raw_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"CSV not found at {path}")
    df = pd.read_csv(path, low_memory=False)
    return df


def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=COLUMN_MAP)

    # Add derived columns
    df["is_winner"] = df["position"] == 1
    df["party_class"] = df["party_type"].fillna("Unknown")
    df["gender"] = df["gender"].str.upper().replace({"FEMALE": "F", "MALE": "M"})
    df["gender"] = df["gender"].fillna("NA")
    df["education"] = df["education"].fillna("Not Available")
    df["candidate_name"] = df["candidate_name"].str.title().str.strip()
    df["state_name"] = df["state_name"].str.replace("_", " ").str.title()
    df["constituency_name"] = df["constituency_name"].str.title()

    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in BOOL_COLS:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .str.lower()
                .map({"true": True, "false": False, "1": True, "0": False})
            )

    df["deposit_lost"] = (
        df["deposit_lost"].astype(str).str.lower().map({"yes": True, "no": False})
    )
    df["deposit_lost"] = df["deposit_lost"].where(df["deposit_lost"].notna(), False).astype(
        bool
    )
    df["turnout_pct"] = df["turnout_pct"].fillna(0)
    df["vote_share_pct"] = df["vote_share_pct"].fillna(0)
    df["margin_pct"] = df["margin_pct"].fillna(0)

    df = df.dropna(subset=["year", "state_name", "constituency_name"])
    df["party"] = df["party"].fillna("IND")
    df = df[(df["year"] >= 1991) & (df["year"] <= 2019)]

    return df


def _create_engine(db_path: Path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    uri = f"sqlite:///{db_path}"
    return create_engine(uri, future=True)


def _write_tables(df: pd.DataFrame, engine) -> None:
    df.to_sql("candidates", engine, if_exists="replace", index=False)

    # Aggregations
    winners = df[df["is_winner"]]
    party_year = (
        winners.groupby(["year", "party", "state_name"], as_index=False)
        .agg(seats=("is_winner", "sum"))
    )
    party_year.to_sql("party_seat_summary", engine, if_exists="replace", index=False)

    turnout = (
        df.drop_duplicates(subset=["year", "state_name", "constituency_name"])
        .groupby(["year", "state_name"], as_index=False)
        .agg(
            turnout_pct=("turnout_pct", "mean"),
            electors=("electors", "sum"),
            valid_votes=("valid_votes", "sum"),
        )
    )
    turnout.to_sql("state_turnout", engine, if_exists="replace", index=False)

    gender = (
        df.groupby(["year", "gender"], as_index=False)
        .agg(
            total_candidates=("candidate_name", "count"),
            total_winners=("is_winner", "sum"),
        )
    )
    gender.to_sql("gender_representation", engine, if_exists="replace", index=False)

    vote_share = (
        df.groupby(["year", "party"], as_index=False)
        .agg(
            total_votes=("votes", "sum"),
        )
    )
    vote_share.to_sql("party_vote_share", engine, if_exists="replace", index=False)

    margin = (
        df[df["is_winner"]]
        .loc[:, ["year", "state_name", "constituency_name", "party", "margin"]]
    )
    margin.to_sql("victory_margins", engine, if_exists="replace", index=False)

    search = df.loc[
        :,
        [
            "year",
            "state_name",
            "constituency_name",
            "candidate_name",
            "party",
            "gender",
            "position",
            "votes",
            "margin",
        ],
    ]
    search.to_sql("candidate_lookup", engine, if_exists="replace", index=False)

    # Views and indices
    with engine.begin() as conn:
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_candidates_year ON candidates(year)"))
        conn.execute(
            text("CREATE INDEX IF NOT EXISTS idx_candidates_state ON candidates(state_name)")
        )
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_candidates_party ON candidates(party)"))
        conn.execute(
            text(
                "CREATE VIEW IF NOT EXISTS party_year_delta AS "
                "WITH seat_counts AS ("
                " SELECT year, party, COUNT(*) AS seats "
                " FROM candidates WHERE is_winner = 1 GROUP BY year, party"
                "), "
                "ranked AS ("
                " SELECT *, LAG(seats) OVER (PARTITION BY party ORDER BY year) AS prev_seats "
                " FROM seat_counts"
                ") "
                "SELECT year, party, seats, COALESCE(seats - prev_seats, 0) AS seat_change "
                "FROM ranked"
            )
        )


def load_database(csv_path: Path = RAW_DATA, db_path: Path = DB_PATH) -> Path:
    df_raw = _load_raw_csv(csv_path)
    df_clean = _clean_dataframe(df_raw)
    engine = _create_engine(db_path)
    _write_tables(df_clean, engine)
    return db_path


def main():
    parser = argparse.ArgumentParser(description="Load Lok Dhaba data into SQLite.")
    parser.add_argument(
        "--csv",
        type=Path,
        default=RAW_DATA,
        help="Path to the All_States_GE CSV export",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DB_PATH,
        help="Path to the SQLite database to create",
    )
    args = parser.parse_args()

    path = load_database(args.csv, args.db)
    print(f"Database created at {path}")


if __name__ == "__main__":
    main()

