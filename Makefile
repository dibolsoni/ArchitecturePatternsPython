export COMPOSE_DOCKER_CLI_BUILD = 1
export DOCKER_BUILDKIT = 1
include .env

all: down build unit-tests integration-tests e2e-tests

build:
	docker-compose build

up:
	docker-compose  up -d app

down:
	docker-compose down -v --remove-orphans

logs:
	docker-compose logs --tail=25 api redis_pubsub

test: unit-tests integration-tests e2e-tests

unit-tests:
	docker-compose run --rm --name unit_tests --entrypoint="pytest /tests/unit -v" tests

integration-tests: restart-db
	docker-compose run --rm --no-deps --name integration_tests --entrypoint="pytest /tests/integration -v" tests

e2e-tests: restart-db
	docker-compose run --rm --name e2e-tests --entrypoint="pytest /tests/e2e -v" tests

restart-db:
	-docker container restart architecture-patterns-db

black:
	black -l 86 $$(find * -name '*.py')
