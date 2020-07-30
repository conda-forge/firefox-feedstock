""" test whether firefox is viable with geckodriver and selenium

    Adaptes from
    https://github.com/conda-forge/firefox-feedstock/blob/master/recipe/run_test.py
"""
import sys
import os
import subprocess
import traceback
import json

from pathlib import Path

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import pytest

FIREFOX = Path(sys.prefix) / "bin" / "firefox"
GECKODRIVER = Path(sys.prefix) / "bin" / "geckodriver"

if "win32" in sys.platform.lower():
    FIREFOX = Path(os.environ["LIBRARY_BIN"]) / "firefox.exe"
    GECKODRIVER = Path(os.environ["SCRIPTS"]) / "geckodriver.exe"


@pytest.mark.parametrize("path,expected_version", [
    [FIREFOX, os.environ["PKG_VERSION"]],
    [GECKODRIVER, None]
])
def test_binary_versions(path, expected_version):
    """ assert that the path exists, is callable, and maybe has the right version
    """
    assert path.exists(), "binary not found"
    version = ""
    subprocess.call([str(path), "--version"])
    proc = subprocess.Popen([str(path), "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()

    for pipe in [stdout, stderr]:
        version += pipe.decode("utf-8") if pipe else ""

    assert version.strip(), "no output received"

    if expected_version:
        assert expected_version in version

def test_read_license(tmp_path):
    geckodriver_log = tmp_path / "geckodriver.log"
    html_log = tmp_path / "license.html"
    license_png = tmp_path / "license.png"

    print("testing about:license with selenium...")
    driver = None
    errors = []
    try:
        options = Options()
        options.headless = True
        options.log_level = "trace"
        driver = webdriver.Firefox(options=options,
                                   firefox_binary=str(FIREFOX),
                                   executable_path=str(GECKODRIVER),
                                   service_log_path=str(geckodriver_log))
        driver.get("about:license")

        if driver.page_source:
            html_log.write_text(driver.page_source)
            assert "Mozilla Public License 2.0" in driver.page_source, \
                "couldn't even load the license page"
            driver.save_screenshot(str(license_png))
            assert license_png.exists()
    except Exception as err:
        print(f"\nEncountered unexpected error: {type(err)} {err}...\n")
        print(traceback.format_exc())
        errors += [err]
    finally:
        errors += list(_dump_logs([geckodriver_log, html_log]))

        if driver:
            driver.quit()

        assert not errors


def _dump_logs(logs):
    for log in logs:
        print(f"Checking {log.name}...\n")
        if log.exists():
            print(log.read_text())
        else:
            yield f"... {log.name} was NOT created!"
        print(f"... end {log.name} check")