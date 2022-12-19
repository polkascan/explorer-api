# Polkascan Explorer API
A GraphQL service that enables subscription-based communication with Polkascan’s data sources.

## Installation
To run the API:

```bash
git clone https://github.com/polkascan/explorer-api.git
cd explorer-api
docker-compose up --build
```

TODO:
https://stackoverflow.com/questions/50387076/docker-compose-conditional-statements-e-g-add-volume-only-if-condition

To run the API with Graphql query logging enabled:
export API_DOCKER_FILE="./docker/api/Dockerfile.query.logging" API_DOCKER_IMAGE="polkascan/explorer-api-query-logging" API_DOCKER_COMMAND="bash -c '/usr/src/start-api-query-logging.sh'" && docker-compose up

To run the API with Telemetry enabled:
https://signoz.io/docs/install/docker/
https://signoz.io/docs/operate/docker-standalone/#remove-the-sample-application
http://localhost:3301/

TODO: mention locust tests


## API Documentation
http://127.0.0.1:8000/graphql

## License
https://github.com/polkascan/explorer-api/blob/master/LICENSE
