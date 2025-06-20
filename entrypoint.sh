#!/bin/sh
set -e

echo "Running data loader..."
python app/load.py

echo "Starting FastAPI app..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload