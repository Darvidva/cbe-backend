# CBE Backend (FastAPI)

## Quickstart
```bash
cd cbe-backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# create .env (see .env.example)
cp .env.example .env  # or copy manually on Windows

# run
uvicorn app.main:app --reload
```

## Default admin
- email: admin@example.com
- password: admin123

Change these in `.env` before first run.
