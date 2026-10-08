#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 was not found. Install Python 3 and run this file again."
  exit 1
fi
python3 -m pip install -r requirements.txt
chmod +x start_netguard.sh
mkdir -p "$HOME/.local/share/applications"
cat > "$HOME/.local/share/applications/netguard-pro.desktop" <<EOF
[Desktop Entry]
Name=NetGuard Pro
Comment=Defensive Network & Security Toolkit
Exec=$PWD/start_netguard.sh
Path=$PWD
Terminal=true
Type=Application
Categories=Network;Security;
EOF
chmod +x "$HOME/.local/share/applications/netguard-pro.desktop"
echo "Installation complete. NetGuard Pro was added to your applications menu."
"$PWD/start_netguard.sh"
