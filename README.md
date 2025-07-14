# Client Installation - x32/x64
```
npm install
npm run dev
```

# Client Installation - ARM / Termux
```
pkg install proot-distro
proot-distro install debian
proot-distro login debian
cd beantrack/beantrack-client
npm install --legacy-peer-deps
NEXT_FORCE_WASM=true npm run dev-arm -- --hostname 0.0.0.0 --port 5482
```

# Server Installation - PowerShell 7
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python server.py
```

# Server Installation - bash
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py
```