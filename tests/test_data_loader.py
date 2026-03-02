"""
Unit tests for the data_loader module.
Tests verify data loading, cleaning, and computation functions.
"""

import pandas as pd
import pytest

from air_passenger_app.data_loader import (
    load_global_departures,
    load_by_region,
    load_by_country,
    compute_yoy_growth,
    compute_seasonal_averages,
    get_available_regions,
    get_available_countries,
)


class TestLoadGlobalDepartures:
    """Tests for load_global_departures()."""

    def test_returns_dataframe(self, df_global):
        assert isinstance(df_global, pd.DataFrame)

    def test_has_required_columns(self, df_global):
        assert {"date", "departures", "year", "month"}.issubset(df_global.columns)

    def test_no_null_departures(self, df_global):
        assert df_global["departures"].isna().sum() == 0

    def test_date_is_datetime(self, df_global):
        assert pd.api.types.is_datetime64_any_dtype(df_global["date"])

    def test_departures_are_positive(self, df_global):
        assert (df_global["departures"] > 0).all()

    def test_year_range(self, df_global):
        assert df_global["year"].min() == 1961
        assert df_global["year"].max() == 2020

    def test_sorted_by_date(self, df_global):
        assert df_global["date"].is_monotonic_increasing


class TestLoadByRegion:
    """Tests for load_by_region()."""

    def test_returns_dataframe(self, df_region):
        assert isinstance(df_region, pd.DataFrame)

    def test_has_required_columns(self, df_region):
        assert {"date", "region", "departures", "year", "month"}.issubset(df_region.columns)

    def test_expected_regions_present(self, df_region):
        expected = {"South East Asia", "Europe", "North America", "Oceania"}
        actual = set(df_region["region"].unique())
        assert expected.issubset(actual)

    def test_no_null_departures(self, df_region):
        assert df_region["departures"].isna().sum() == 0

    def test_eight_regions(self, df_region):
        assert df_region["region"].nunique() == 8


class TestLoadByCountry:
    """Tests for load_by_country()."""

    def test_returns_dataframe(self, df_country):
        assert isinstance(df_country, pd.DataFrame)

    def test_has_required_columns(self, df_country):
        assert {"date", "region", "country", "departures"}.issubset(df_country.columns)

    def test_eleven_countries(self, df_country):
        assert df_country["country"].nunique() == 11

    def test_no_null_departures(self, df_country):
        assert df_country["departures"].isna().sum() == 0


class TestComputeYoYGrowth:
    """Tests for compute_yoy_growth()."""

    def test_returns_dataframe(self, df_yoy):
        assert isinstance(df_yoy, pd.DataFrame)

    def test_has_growth_column(self, df_yoy):
        assert "yoy_growth" in df_yoy.columns

    def test_first_row_growth_is_nan(self, df_yoy):
        # First year has no prior year to compare
        assert pd.isna(df_yoy["yoy_growth"].iloc[0])

    def test_growth_values_are_numeric(self, df_yoy):
        non_null = df_yoy["yoy_growth"].dropna()
        assert pd.api.types.is_float_dtype(non_null)

    def test_large_drop_in_2020(self, df_yoy):
        """2020 should show a significant negative growth due to COVID-19."""
        growth_2020 = df_yoy.loc[df_yoy["year"] == 2020, "yoy_growth"].values[0]
        assert growth_2020 < 0


class TestComputeSeasonalAverages:
    """Tests for compute_seasonal_averages()."""

    def test_returns_twelve_months(self, df_seasonal):
        assert len(df_seasonal) == 12

    def test_has_month_name_column(self, df_seasonal):
        assert "month_name" in df_seasonal.columns

    def test_all_months_present(self, df_seasonal):
        expected = {"Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"}
        assert set(df_seasonal["month_name"]) == expected

    def test_average_departures_positive(self, df_seasonal):
        assert (df_seasonal["departures"] > 0).all()


class TestGetAvailableRegions:
    """Tests for get_available_regions()."""

    def test_returns_list(self, df_region):
        result = get_available_regions(df_region)
        assert isinstance(result, list)

    def test_list_is_sorted(self, df_region):
        result = get_available_regions(df_region)
        assert result == sorted(result)

    def test_eight_regions_returned(self, df_region):
        result = get_available_regions(df_region)
        assert len(result) == 8


class TestGetAvailableCountries:
    """Tests for get_available_countries()."""

    def test_returns_list(self, df_country):
        result = get_available_countries(df_country)
        assert isinstance(result, list)

    def test_list_is_sorted(self, df_country):
        result = get_available_countries(df_country)
        assert result == sorted(result)

    def test_eleven_countries(self, df_country):
        result = get_available_countries(df_country)
        assert len(result) == 11
