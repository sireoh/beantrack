# Client Installation - x32/x64 🚀 Windows
```
npm install
npm run dev
```

# Client Installation - ARM 🚀 Termux
```
pkg install proot-distro
proot-distro install debian
proot-distro login debian
cd beantrack/beantrack-client
npm install --legacy-peer-deps
NEXT_FORCE_WASM=true npm run dev-arm -- --hostname 0.0.0.0 --port 5482
```

# Server Installation - PowerShell 7 🚀 Windows
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python server.py
```

# Server Installation - bash 🚀 Termux
```
pkg install proot-distro
proot-distro install debian
proot-distro login debian
apt update
apt install curl build-essential
curl https://sh.rustup.rs -sSf | sh
```
You can add `source $HOME/.cargo/env` to your ~/.bashrc or ~/.profile for persistence.

Verify:
```
rustc --version
cargo --version
```
Continue Installation:
```
apt update && apt upgrade
apt install python3 python3-venv python3-pip
python -m venv .venv
source .venv/bin/activate
```
Upgrade Dependencies:
```
pip install --upgrade pip setuptools wheel
```
Continue Installation:
```
pip install -r requirements.txt
python server.py
```