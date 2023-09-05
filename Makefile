export COMPOSE_DOCKER_CLI_BUILD = 1
export DOCKER_BUILDKIT = 1

all: down build unit-tests integration-tests e2e-tests

build:
	docker-compose build

up:
	docker-compose  up -d app

down:
	docker-compose down

logs:
	docker-compose logs app | tail -100

unit-tests:
	docker-compose run --rm --no-deps --name unit_tests --entrypoint=pytest app /tests/unit

integration-tests: up
	docker-compose run --rm --no-deps --name integration_tests --entrypoint=pytest app /tests/integration

e2e-tests: up
	docker-compose run --rm --no-deps --name e2e_tests --entrypoint=pytest app /tests/e2e

black:
	black -l 86 $$(find * -name '*.py')
