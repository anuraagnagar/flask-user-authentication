#!/bin/bash
set -e

SERVER_HOST=0.0.0.0
SERVER_PORT=5000

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL at $POSTGRES_HOST:$POSTGRES_PORT..."

until nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  sleep 1
done

echo -e "✅ PostgreSQL is available."

# Conditionally create the database if it doesn't exist
echo -e "🔍 Checking if database '${POSTGRES_DB}' exists..."
DB_EXISTS=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -tc "SELECT 1 FROM pg_database WHERE datname = '${POSTGRES_DB}'" postgres | tr -d '[:space:]')

if [ "$DB_EXISTS" != "1" ]; then
  echo -e "🛠 Creating database '${POSTGRES_DB}'..."
  PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -c "CREATE DATABASE ${POSTGRES_DB};" postgres
  echo -e "✅ Database '${POSTGRES_DB}' created successfully."
else
  echo -e "✅ Database '${POSTGRES_DB}' already exists."
fi

if [ ! -d "migrations" ]; then
  echo -e "Running initial migrations..."
  # create migration directory
  flask db init

  # Run migrations and make changes
  flask db migrate -m "initial migration"
  flask db upgrade
else
  echo -e "🔍 Checking for any changes in database tables..."
  if flask db check > /dev/null 2>&1; then
    echo -e "✅ No changes detected. Your database is up to date."
  else
    echo -e "🆕 Changes detected. Running migrations and upgrade..."
    flask db migrate -m "auto migration"
    flask db upgrade
  fi
fi

# Create test user (our custom command for creating initial test user)
echo -e "Creating test user..."
flask createtestuser

# Start the Flask app
echo -e "Starting the Flask application..."
exec flask run --host=$SERVER_HOST --port=$SERVER_PORT
