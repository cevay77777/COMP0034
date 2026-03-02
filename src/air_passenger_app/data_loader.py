"""
Data loading and processing module for Singapore Air Passenger Departures dataset.
Source: https://data.gov.sg/dataset/air-passenger-departures-total-by-region-and-selected-country
"""

import pandas as pd
from pathlib import Path

# Resolve data directory relative to this file
DATA_DIR = Path(__file__).parent.parent.parent / "data"


def load_global_departures() -> pd.DataFrame:
    """Load and clean the global monthly air passenger departures data.

    Returns:
        pd.DataFrame: Cleaned dataframe with columns ['date', 'departures'].
    """
    df = pd.read_csv(DATA_DIR / "TotalAirPassengerDepartures.csv")
    df = df.rename(columns={"month": "date", "value": "departures"})
    df = df[["date", "departures"]].copy()
    df["departures"] = pd.to_numeric(df["departures"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna(subset=["departures"])
    df = df.sort_values("date").reset_index(drop=True)
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    return df


def load_by_region() -> pd.DataFrame:
    """Load and clean air passenger departures broken down by region.

    Returns:
        pd.DataFrame: Cleaned dataframe with columns ['date', 'region', 'departures'].
    """
    df = pd.read_csv(DATA_DIR / "TotalAirPassengerDeparturesbyRegion.csv")
    df = df.rename(columns={"month": "date", "level_2": "region", "value": "departures"})
    df = df[["date", "region", "departures"]].copy()
    df["departures"] = pd.to_numeric(df["departures"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna(subset=["departures"])
    df = df.sort_values("date").reset_index(drop=True)
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    return df


def load_by_country() -> pd.DataFrame:
    """Load and clean air passenger departures broken down by country.

    Returns:
        pd.DataFrame: Cleaned dataframe with columns ['date', 'region', 'country', 'departures'].
    """
    df = pd.read_csv(DATA_DIR / "TotalAirPassengerDeparturesbyCountry.csv")
    df = df.rename(
        columns={
            "month": "date",
            "level_2": "region",
            "level_3": "country",
            "value": "departures",
        }
    )
    df = df[["date", "region", "country", "departures"]].copy()
    df["departures"] = pd.to_numeric(df["departures"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna(subset=["departures"])
    df = df.sort_values("date").reset_index(drop=True)
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    return df


def compute_yoy_growth(df: pd.DataFrame) -> pd.DataFrame:
    """Compute year-on-year percentage growth from global departures data.

    Args:
        df: Output of load_global_departures().

    Returns:
        pd.DataFrame: Annual totals with a yoy_growth column (%).
    """
    annual = df.groupby("year")["departures"].sum().reset_index()
    annual = annual.rename(columns={"departures": "total_departures"})
    annual["yoy_growth"] = annual["total_departures"].pct_change() * 100
    return annual


def compute_seasonal_averages(df: pd.DataFrame) -> pd.DataFrame:
    """Compute average monthly departures to reveal seasonal patterns.

    Args:
        df: Output of load_global_departures().

    Returns:
        pd.DataFrame: Average departures per calendar month (1–12).
    """
    month_names = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
        5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
        9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
    }
    seasonal = df.groupby("month")["departures"].mean().reset_index()
    seasonal["month_name"] = seasonal["month"].map(month_names)
    return seasonal


def get_available_regions(df: pd.DataFrame) -> list:
    """Return sorted list of unique region names.

    Args:
        df: Output of load_by_region().

    Returns:
        list: Sorted unique region names.
    """
    return sorted(df["region"].unique().tolist())


def get_available_countries(df: pd.DataFrame) -> list:
    """Return sorted list of unique country names.

    Args:
        df: Output of load_by_country().

    Returns:
        list: Sorted unique country names.
    """
    return sorted(df["country"].unique().tolist())
