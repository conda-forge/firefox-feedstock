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

if "win32" in sys.platform.lower():
    FIREFOX = Path(os.environ["LIBRARY_BIN"]) / "firefox.exe"
    GECKODRIVER = Path(os.environ["SCRIPTS"]) / "geckodriver.exe"
else:
    FIREFOX = Path(sys.prefix) / "bin" / "firefox"
    GECKODRIVER = Path(sys.prefix) / "bin" / "geckodriver"


@pytest.mark.parametrize("path,expected_version", [
    [FIREFOX, os.environ["PKG_VERSION"]],
    [GECKODRIVER, None]
])
def test_binary_versions(path, expected_version, allow_call_fail):
    """ assert that the path exists, is callable, and maybe has the right version
    """
    assert path.exists(), "binary not found"
    version = ""
    subprocess.call([str(path), "--version"])
    proc = subprocess.Popen([str(path), "--version"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, stderr = proc.communicate()

    for pipe in [stdin, stdout]:
        version += pipe.read().decode("utf-8") if pipe else ""

    assert version.strip(), "no output received"

    if expected_version:
        assert expected_version in version

def test_read_license(tmp_path):
    geckodriver_log = tmp_path / "geckodriver.log"
    firefox_log = tmp_path / "firefox.log"
    html_log = tmp_path / "license.html"

    print("testing about:license with selenium...")
    driver = None
    errors = []
    try:
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(options=options,
                                   firefox_binary=str(FIREFOX),
                                   executable_path=str(GECKODRIVER),
                                   service_log_path=str(geckodriver_log),
                                   log_path=str(firefox_log))
        driver.get("about:license")

        if driver.page_source:
            html_log.write_text(driver.page_source)
            assert "Mozilla Public License 2.0" in driver.page_source, \
                "couldn't even load the license page"
    except Exception as err:
        print(f"\nEncountered unexpected error: {type(err)} {err}...\n")
        print(traceback.format_exc())
        if IGNORE_FIREFOX_FAIL:
            print("... about:license check ignored because of expected Firefox fail")
            return_code = 0
        else:
            errors += [err]
    finally:
        errors += list(_dump_logs([firefox_log, geckodriver_log, html_log]))

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
