#!/usr/bin/env bash
set -eux -o pipefail

_UNAME=$(uname)

APP_DIR="${PREFIX}/bin/Firefox.app"
LAUNCH_SCRIPT="${PREFIX}/bin/firefox"

mkdir -p "${APP_DIR}"

if [[ "${_UNAME}" == "Linux" ]]; then
  mv firefox/* "${APP_DIR}"
  BIN_LOCATION="${APP_DIR}/firefox"
  ICON_LOCATION="${APP_DIR}/browser/chrome/icons/default/default128.png"
  ICON_EXT="png"
elif [[ "${_UNAME}" == "Darwin" ]]; then
  pkgutil --expand-full firefox.pkg firefox
  cp -rf firefox/Firefox.pkg/Payload/Firefox.app/* "${APP_DIR}"
  BIN_LOCATION="${APP_DIR}/Contents/MacOS/firefox"
  ICON_LOCATION="${APP_DIR}/Contents/Resources/firefox.icns"
  ICON_EXT="icns"
fi

# Write launch script and make executable
cat <<EOF >"${LAUNCH_SCRIPT}"
#!/usr/bin/env bash
"${BIN_LOCATION}" "\$@"
EOF

chmod +x "${LAUNCH_SCRIPT}"

# Install menuinst shortcut
mkdir -p "${PREFIX}/Menu"
install -m0644 "${ICON_LOCATION}" "${PREFIX}/Menu/firefox.${ICON_EXT}"
sed -e "s/__PKG_VERSION__/${PKG_VERSION}/g" "${RECIPE_DIR}/menu.json" >"${PREFIX}/Menu/${PKG_NAME}_menu.json"
