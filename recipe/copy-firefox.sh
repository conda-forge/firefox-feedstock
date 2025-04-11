#!/usr/bin/env bash
set -eux -o pipefail

_UNAME=$(uname)

APP_DIR="${PREFIX}/bin/FirefoxApp"
LAUNCH_SCRIPT="${PREFIX}/bin/firefox"

mkdir -p "${APP_DIR}"

if [[ "${_UNAME}" == "Linux" ]]; then
  mv firefox/* "${APP_DIR}"
  BIN_LOCATION="${APP_DIR}/firefox"
elif [[ "${_UNAME}" == "Darwin" ]]; then
  pkgutil --expand firefox.pkg firefox
  cpio -i -I firefox/*/Payload
  cp -rf Firefox.app/* "${APP_DIR}"
  BIN_LOCATION="${APP_DIR}/Contents/MacOS/firefox"
fi

# Write launch script and make executable
cat <<EOF >"${LAUNCH_SCRIPT}"
#!/bin/bash
"${BIN_LOCATION}" "\$@"
EOF

chmod +x "${LAUNCH_SCRIPT}"
