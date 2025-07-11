# Client Installation - x32/x64
```
npm install
npm run dev
```

# Client Installation - ARM
```
npm install
NEXT_FORCE_WASM=true npm run dev-arm -- --hostname 0.0.0.0 --port 5482
```

# Server Installation
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```