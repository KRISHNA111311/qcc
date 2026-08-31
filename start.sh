# Start the QCC backend locally (requires PostgreSQL running)
poetry run uvicorn src.qcc.main:app --reload
