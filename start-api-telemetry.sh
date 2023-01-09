# If there's a prestart.sh script in the /app directory, run it before starting
source ./prestart.sh
# Execute DB migrations
alembic upgrade head
# Import assets
python app/import_assets.py
# Start Uvicorn with live reload

export OTEL_RESOURCE_ATTRIBUTES=service.name=explorer-api OTEL_EXPORTER_OTLP_ENDPOINT="http://clickhouse-setup_otel-collector_1:4318" OTEL_TRACES_EXPORTER=otlp
exec opentelemetry-instrument --traces_exporter otlp_proto_http --metrics_exporter otlp_proto_http uvicorn --host 0.0.0.0 --port 8000 --log-level info "app.main:app" --forwarded-allow-ips='*' --proxy-headers