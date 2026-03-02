"""Pytest configuration and shared fixtures."""

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import threading
import time

from air_passenger_app.app import app
from air_passenger_app.data_loader import (
    load_global_departures,
    load_by_region,
    load_by_country,
    compute_yoy_growth,
    compute_seasonal_averages,
)


@pytest.fixture(scope="session")
def df_global():
    return load_global_departures()


@pytest.fixture(scope="session")
def df_region():
    return load_by_region()


@pytest.fixture(scope="session")
def df_country():
    return load_by_country()


@pytest.fixture(scope="session")
def df_yoy(df_global):
    return compute_yoy_growth(df_global)


@pytest.fixture(scope="session")
def df_seasonal(df_global):
    return compute_seasonal_averages(df_global)


@pytest.fixture(scope="session")
def dash_app():
    """Start the Dash app in a background thread for Selenium tests."""
    server = app.server

    def run():
        app.run(debug=False, port=8050, use_reloader=False)

    t = threading.Thread(target=run, daemon=True)
    t.start()
    time.sleep(2)  # Give server time to start
    yield "http://localhost:8050"


@pytest.fixture(scope="session")
def driver():
    """Provide a headless Chrome WebDriver."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,900")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()
