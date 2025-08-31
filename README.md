## 🚀 Automated Selenium & WebDriver Setup Script

## Overview

`setup_selenium.py` is a Python script that automates the installation of Selenium and WebDriver Manager, detects your installed browser (Chrome or Firefox), and runs a smoke test to verify Selenium is working. It supports headless mode, saves screenshots on success or failure, and logs output for troubleshooting.

---

## Features

- Installs `selenium` and `webdriver-manager` (unless `--no-install` is used)
- Auto-detects Chrome or Firefox browser
- Supports headless mode via CLI or `HEADLESS` environment variable
- Runs a smoke test by loading a test URL and waiting for a search box
- Saves screenshots to the `screenshots/` directory
- Logs pip and exception output to `setup_selenium.log`
- Command-line options for browser, headless mode, retries, and test URL

---

## Requirements

- Python 3.6+
- **Chrome or Firefox browser** installed (at least one)
- Internet connection (for installation and driver download)

---

## Installation

No installation required.  
Just download `setup_selenium.py` and run it with Python.

---

## How to Use

Open a terminal or command prompt and run:

```sh
python setup_selenium.py [options]
```

### Options

- `--browser chrome|firefox`  
  Choose browser for the test (default: auto-detected or Chrome)
- `--headless`  
  Run browser in headless mode (default: True)
- `--no-headless`  
  Run browser with UI
- `--no-install`  
  Skip pip install step (useful in virtual environments)
- `--test-url URL`  
  URL to use for the smoke test (default: https://www.google.com)
- `--install-retries N`  
  Number of retries for pip install (default: 3)
- `--test-retries N`  
  Number of retries for the Selenium test (default: 2)

### Example Usage

Run a smoke test in Chrome, headless mode:

```sh
python setup_selenium.py --browser chrome --headless
```

Run a smoke test in Firefox with UI:

```sh
python setup_selenium.py --browser firefox --no-headless
```

Test a custom URL:

```sh
python setup_selenium.py --test-url https://example.com
```

Skip package installation (if already installed):

```sh
python setup_selenium.py --no-install
```

---

## Output

- Screenshots saved in `screenshots/`
- Logs saved in `setup_selenium.log`

---

## Troubleshooting

- Check `setup_selenium.log` for detailed error messages.
- Ensure your browser is installed and accessible in your system PATH.

