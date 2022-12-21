# Polkascan Explorer API
A GraphQL service that enables subscription-based communication with Polkascan’s data sources.

## Installation
To run the API:

```bash
git clone https://github.com/polkascan/explorer-api.git
cd explorer-api
docker-compose up --build
```

## Interactive playground to execute queries and read it's API specification
```bash
http://127.0.0.1:8000/graphql
```

# Add GraphQL query logging

To run the API with GraphQL query logging enabled, we should run docker-compose with the following environment variables set:
```bash
export API_DOCKER_FILE="./docker/api/Dockerfile.query.logging" API_DOCKER_IMAGE="polkascan/explorer-api-query-logging" API_DOCKER_COMMAND="bash -c '/usr/src/start-api-query-logging.sh'" && docker-compose up --build
```

This will override the dockerfile used by default for the API. When the api is run in this mode, it will store all raw graphql queries in a csv file called "api_query_log.csv", this log file will be rotated every day to keep it's size manageable. This can be used to monitor API usage without impacting performance too much. In our case, we use these logs to analyse & replay all queries against a dedicated test server. 

When we login to our explorer-api docker instance, we can see the generates log file after running http or websocket queries:
```bash
docker exec -it explorer-api_api_1 /bin/bash
cat api_query_log.csv
```

# Add telemetry using Signoz

To run the API with telemetry tracing enabled, we first need to install Signoz:
https://signoz.io/docs/install/docker/

Note: If you want to remove the sample application, follow these steps to modify the Signoz docker-compose file:
https://signoz.io/docs/operate/docker-standalone/#remove-the-sample-application

```bash
git clone -b main https://github.com/SigNoz/signoz.git && cd signoz/deploy/

nano docker/clickhouse-setup/docker-compose.yaml
remove or comment sections hotrod & load-hotrod ath the bottom of the file

./install.sh

docker-compose -f docker/clickhouse-setup/docker-compose.yaml up -d
```

Next in the explorer-api/docker-compose.yml, in the api section, uncomment these lines:

```bash
    networks:
        - default
        - clickhouse-setup_default
```

And in the networks section, uncomment these lines:

```bash
networks:
    clickhouse-setup_default: # external network (app1)
        external: true
```

Note: By default, start-api-telemetry.sh will be called from the accompanying dockerfile (docker/api/Dockerfile.telemetry), using these environment variables:
```bash
    OTEL_EXPORTER_OTLP_ENDPOINT='http://clickhouse-setup_default:4317'
    OTEL_RESOURCE_ATTRIBUTES='service.name=explorer-api'
    OTEL_TRACES_EXPORTER=otlp
```


Now we can build the explorer-api by using the telemetry specific variables set and run it:
```bash
export API_DOCKER_FILE="./docker/api/Dockerfile.telemetry" API_DOCKER_IMAGE="polkascan/explorer-api-telemetry" API_DOCKER_COMMAND="bash -c '/usr/src/start-api-telemetry.sh'" && docker-compose up --build
```

After running some graphql queries we can examine the traces in the Signoz dashboard:
http://localhost:3301/

# Synthetic load tests using Locust

To create some requests, we can use Locust.

## Install Locust
```bash
pip3 install locust
```

## Run it with a GUI
```bash
locust -f tests/test_http.py
locust -f tests/test_websockets.py
```

## Run it using the commandline
```bash
locust -f tests/test_http.py -u 1 -r 10 --headless --run-time 30s
locust -f tests/test_websockets.py -u 1 -r 10 -t 10 --headless --run-time 30s
```

## License
https://github.com/polkascan/explorer-api/blob/master/LICENSE
