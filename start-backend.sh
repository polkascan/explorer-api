# If there's a prestart.sh script in the /app directory, run it before starting
source ./prestart.sh
# Start Uvicorn with live reload
exec uvicorn --reload --host 0.0.0.0 --port 8000 --log-level debug "app.main:app"