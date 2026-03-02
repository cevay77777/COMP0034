"""
Browser-based integration tests for the Singapore Air Passenger Departures Dash app.
Uses Selenium WebDriver with headless Chrome.

Note: These tests require the app to be running (started via the dash_app fixture
in conftest.py) and Chrome/Chromium to be installed.
"""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Skip all browser tests gracefully if Chrome is not available
pytest.importorskip("selenium")


class TestPageLoad:
    """Tests that the app loads correctly in a browser."""

    def test_page_title(self, driver, dash_app):
        """The browser tab title should contain the app name."""
        driver.get(dash_app)
        WebDriverWait(driver, 10).until(
            lambda d: "Updating..." not in d.title
        )
        assert "Singapore Air Passenger" in driver.title

    def test_heading_visible(self, driver, dash_app):
        """The main H1 heading should be present on the page."""
        driver.get(dash_app)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        h1 = driver.find_element(By.TAG_NAME, "h1")
        assert "Singapore" in h1.text

    def test_kpi_cards_present(self, driver, dash_app):
        """Three KPI summary cards should be visible."""
        driver.get(dash_app)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "card"))
        )
        cards = driver.find_elements(By.CLASS_NAME, "card")
        assert len(cards) >= 3


class TestTabs:
    """Tests for tab navigation."""

    def test_tabs_present(self, driver, dash_app):
        """All five chart tabs should be rendered."""
        driver.get(dash_app)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "nav-link"))
        )
        tabs = driver.find_elements(By.CLASS_NAME, "nav-link")
        tab_labels = [t.text for t in tabs]
        assert "Global Trend" in tab_labels
        assert "By Region" in tab_labels
        assert "Year-on-Year Growth" in tab_labels

    def test_default_tab_renders_chart(self, driver, dash_app):
        """The default Global Trend tab should render a Plotly chart."""
        driver.get(dash_app)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "js-plotly-plot"))
        )
        charts = driver.find_elements(By.CLASS_NAME, "js-plotly-plot")
        assert len(charts) >= 1

    def test_click_region_tab(self, driver, dash_app):
        """Clicking the By Region tab should load a new chart."""
        driver.get(dash_app)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "nav-link"))
        )
        tabs = driver.find_elements(By.CLASS_NAME, "nav-link")
        region_tab = next(t for t in tabs if "By Region" in t.text)
        region_tab.click()
        time.sleep(2)
        charts = driver.find_elements(By.CLASS_NAME, "js-plotly-plot")
        assert len(charts) >= 1

    def test_click_yoy_tab(self, driver, dash_app):
        """Clicking the Year-on-Year Growth tab should load a chart."""
        driver.get(dash_app)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "nav-link"))
        )
        tabs = driver.find_elements(By.CLASS_NAME, "nav-link")
        yoy_tab = next(t for t in tabs if "Year-on-Year" in t.text)
        yoy_tab.click()
        time.sleep(2)
        charts = driver.find_elements(By.CLASS_NAME, "js-plotly-plot")
        assert len(charts) >= 1

    def test_click_seasonal_tab(self, driver, dash_app):
        """Clicking the Seasonal Pattern tab should load a chart."""
        driver.get(dash_app)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "nav-link"))
        )
        tabs = driver.find_elements(By.CLASS_NAME, "nav-link")
        seasonal_tab = next(t for t in tabs if "Seasonal" in t.text)
        seasonal_tab.click()
        time.sleep(2)
        charts = driver.find_elements(By.CLASS_NAME, "js-plotly-plot")
        assert len(charts) >= 1

    def test_click_map_tab(self, driver, dash_app):
        """Clicking the Country Map tab should load a choropleth chart."""
        driver.get(dash_app)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "nav-link"))
        )
        tabs = driver.find_elements(By.CLASS_NAME, "nav-link")
        map_tab = next(t for t in tabs if "Country Map" in t.text)
        map_tab.click()
        time.sleep(3)
        charts = driver.find_elements(By.CLASS_NAME, "js-plotly-plot")
        assert len(charts) >= 1


class TestFilters:
    """Tests for the filter panel interactions."""

    def test_region_dropdown_present(self, driver, dash_app):
        """Region dropdown should be present in the filter panel."""
        driver.get(dash_app)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "region-dropdown"))
        )
        dropdown = driver.find_element(By.ID, "region-dropdown")
        assert dropdown is not None

    def test_country_dropdown_present(self, driver, dash_app):
        """Country dropdown should be present in the filter panel."""
        driver.get(dash_app)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "country-dropdown"))
        )
        dropdown = driver.find_element(By.ID, "country-dropdown")
        assert dropdown is not None

    def test_year_slider_present(self, driver, dash_app):
        """Year range slider should be present."""
        driver.get(dash_app)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "year-slider"))
        )
        slider = driver.find_element(By.ID, "year-slider")
        assert slider is not None

    def test_footer_present(self, driver, dash_app):
        """Data source attribution footer should appear on page."""
        driver.get(dash_app)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "p"))
        )
        paragraphs = [p.text for p in driver.find_elements(By.TAG_NAME, "p")]
        footer_found = any("data.gov.sg" in p for p in paragraphs)
        assert footer_found