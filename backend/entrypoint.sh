#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Waiting for PgBouncer to be ready..."
# We assume the pgbouncer service is named 'pgbouncer' and is available on port 6432
while ! nc -z pgbouncer 6432; do
  sleep 1
done
echo "PgBouncer is ready!"

echo "Running database seeding..."
python seed_db.py

echo "Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
