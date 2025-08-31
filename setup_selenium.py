#!/usr/bin/env python3
"""
Automatic Selenium Installation & Smoke Test Script
Features:
 - Installs selenium + webdriver-manager (unless --no-install)
 - Auto-detects installed browser (chrome/firefox) if --browser not provided
 - Supports HEADLESS env var and --headless/--no-headless flags
 - Runs a simple smoke test (loads TEST_URL, waits for search box by name 'q')
 - Saves screenshots to screenshots/ on success or failure
 - Writes pip and exception output to setup_selenium.log
"""

import sys
import subprocess
import os
import time
from urllib.request import urlopen
import logging
import shutil
from pathlib import Path

# -------------------- Logging Setup --------------------
import logging as py_logging
py_logging.getLogger("WDM").setLevel(py_logging.ERROR)  # Suppress webdriver-manager INFO logs

LOGFILE = "setup_selenium.log"
logging.basicConfig(filename=LOGFILE, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# -------------------- Console Output Helpers --------------------
def print_color(text, color_code):
    # Print colored text to the console using ANSI escape codes
    print(f"\033[{color_code}m{text}\033[0m")

def print_success(text):
    # Print success message in green and log it
    print_color(f"✅ {text}", "32")
    logging.info(text)

def print_error(text):
    # Print error message in red and log it
    print_color(f"❌ {text}", "31")
    logging.error(text)

def print_info(text):
    # Print info message in blue and log it
    print_color(f"ℹ️ {text}", "34")
    logging.info(text)

# -------------------- Utility / Checks --------------------
SCREENSHOT_DIR = Path("screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)  # Ensure screenshot directory exists

def save_screenshot(driver, name_prefix: str):
    # Save a screenshot from the Selenium driver with a timestamped filename
    ts = int(time.time())
    path = SCREENSHOT_DIR / f"{name_prefix}_{ts}.png"
    try:
        driver.save_screenshot(str(path))
        return path
    except Exception as e:
        logging.exception("Failed to save screenshot")
        return None

def check_internet():
    # Check for internet connectivity by trying to reach Google
    try:
        urlopen("https://www.google.com", timeout=5)
        return True
    except Exception as e:
        print_error(f"Internet connection error: {e}")
        return False

def check_python_version():
    # Ensure Python version is at least 3.6
    if sys.version_info < (3, 6):
        print_error("Python 3.6 or higher is required.")
        return False
    print_success(f"Python version: {sys.version}")
    return True

def detect_browser():
    """
    Try to detect an installed browser executable.
    Prefer Chrome/Chromium over Firefox when both present.
    """
    candidates = [
        ("chrome", ["google-chrome", "chrome", "chromium", "chromium-browser"]),
        ("firefox", ["firefox"])
    ]
    for name, bins in candidates:
        for b in bins:
            if shutil.which(b):
                logging.info(f"Detected browser binary '{b}' -> choosing {name}")
                return name
    logging.info("No browser binary detected from PATH")
    return None

# -------------------- Installation --------------------
def install_packages(retries=3):
    """
    Install selenium and webdriver-manager via pip.
    Pip output is redirected to the log file to keep console tidy.
    Retries installation up to 'retries' times if it fails.
    """
    for attempt in range(1, retries + 1):
        try:
            print_info("Installing selenium and webdriver-manager (pip)...")
            with open(LOGFILE, "a") as lf:
                subprocess.run([
                    sys.executable, "-m", "pip", "install",
                    "selenium", "webdriver-manager", "--quiet"
                ], stdout=lf, stderr=lf, check=True)
            print_success("Packages installed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print_error(f"Attempt {attempt}: Failed to install packages (see {LOGFILE})")
            logging.exception("pip install failed")
            if attempt < retries:
                print_info("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                return False

# -------------------- Selenium Smoke Test --------------------
def test_selenium(browser="chrome", headless=True, test_url="https://www.google.com", retries=2, wait_secs=10):
    """
    Launch chosen browser, visit test_url and wait for element name='q' (Google search box).
    Saves a screenshot on success and on failure attempts.
    Retries the test up to 'retries' times if it fails.
    """
    for attempt in range(1, retries + 1):
        driver = None
        try:
            # Import Selenium modules only when needed
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            # Setup browser-specific options and driver
            if browser.lower() == "chrome":
                from selenium.webdriver.chrome.service import Service as ChromeService
                from selenium.webdriver.chrome.options import Options as ChromeOptions
                from webdriver_manager.chrome import ChromeDriverManager

                options = ChromeOptions()
                if headless:
                    # Use new headless mode if available
                    try:
                        options.add_argument("--headless=new")
                    except Exception:
                        options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")

                service = ChromeService(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)

            elif browser.lower() == "firefox":
                from selenium.webdriver.firefox.service import Service as FirefoxService
                from selenium.webdriver.firefox.options import Options as FirefoxOptions
                from webdriver_manager.firefox import GeckoDriverManager

                options = FirefoxOptions()
                options.headless = bool(headless)
                options.add_argument("--width=1920")
                options.add_argument("--height=1080")

                service = FirefoxService(GeckoDriverManager().install())
                driver = webdriver.Firefox(service=service, options=options)

            else:
                print_error(f"Unsupported browser: {browser}. Choose 'chrome' or 'firefox'.")
                return False

            print_info(f"Launching {browser} (headless={headless}) and loading {test_url} ...")
            driver.set_page_load_timeout(30)
            driver.get(test_url)

            # Wait for the search box element to appear
            WebDriverWait(driver, wait_secs).until(EC.presence_of_element_located((By.NAME, "q")))

            # Save screenshot on success
            success_path = save_screenshot(driver, f"selenium_success_{browser}")
            if success_path:
                print_success(f"Selenium smoke test passed. Screenshot: {success_path}")
            else:
                print_success("Selenium smoke test passed (screenshot failed).")

            driver.quit()
            return True

        except Exception as e:
            print_error(f"Attempt {attempt}: Selenium test failed: {e}")
            logging.exception("Selenium exception")
            try:
                if driver:
                    # Save screenshot on failure
                    fail_path = save_screenshot(driver, f"selenium_fail_{browser}_attempt{attempt}")
                    if fail_path:
                        print_info(f"Saved failure screenshot: {fail_path}")
                    driver.quit()
            except Exception:
                logging.exception("Error while handling failed driver")

            if attempt < retries:
                print_info("Retrying Selenium test in 3 seconds...")
                time.sleep(3)
            else:
                return False

# -------------------- Main --------------------
def main():
    import argparse

    # Determine default headless mode from environment variable
    env_headless = os.environ.get("HEADLESS")
    if env_headless is None:
        default_headless = True  # Default to headless
    else:
        default_headless = env_headless not in ("0", "false", "False", "FALSE")

    # Detect browser from environment or system
    detected = detect_browser()
    env_browser = os.environ.get("SEL_BROWSER")
    default_browser = env_browser or detected or "chrome"

    # Setup command-line argument parsing
    parser = argparse.ArgumentParser(description="Install Selenium and run a basic smoke test.")
    parser.add_argument("--browser", choices=["chrome", "firefox"], default=default_browser,
                        help=f"Browser to test (default: env SEL_BROWSER or detected or 'chrome'). Detected: {detected}")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--headless", dest="headless", action="store_true", help="Run browser in headless mode.")
    group.add_argument("--no-headless", dest="headless", action="store_false", help="Run browser with UI.")
    parser.set_defaults(headless=default_headless)

    parser.add_argument("--no-install", action="store_true", help="Skip pip install step (useful in venv).")
    parser.add_argument("--test-url", default=os.environ.get("TEST_URL", "https://www.google.com"),
                        help="URL to use for the smoke test (default: https://www.google.com or TEST_URL env).")
    parser.add_argument("--install-retries", default=3, type=int, help="Retries for pip install.")
    parser.add_argument("--test-retries", default=2, type=int, help="Retries for the selenium test.")
    args = parser.parse_args()

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Check internet connectivity
    if not check_internet():
        print_error("Internet is required to install drivers/packages (or to download drivers).")
        sys.exit(1)

    # Install required packages unless --no-install is specified
    if not args.no_install:
        if not install_packages(retries=args.install_retries):
            print_error("Failed to install required packages. See setup_selenium.log for details.")
            sys.exit(1)
    else:
        print_info("Skipping package installation (--no-install).")

    chosen_browser = args.browser
    print_info(f"Using browser: {chosen_browser} (headless={args.headless})")

    # Run the Selenium smoke test
    success = test_selenium(browser=chosen_browser, headless=args.headless,
                           test_url=args.test_url, retries=args.test_retries)

    if success:
        print_success("All done — Selenium smoke test succeeded.")
        sys.exit(0)
    else:
        print_error("Selenium smoke test failed. See setup_selenium.log and screenshots/ for details.")
        sys.exit(2)

if __name__ == "__main__":
    main()