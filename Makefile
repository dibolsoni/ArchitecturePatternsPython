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

test: restart-db unit-tests integration-tests e2e-tests

unit-tests:
	docker-compose run --rm --no-deps --name unit_tests --entrypoint="pytest /tests/unit -vv" tests

integration-tests:
	docker-compose run --rm --no-deps --name integration_tests --entrypoint="pytest /tests/integration -vv" tests

e2e-tests:
	docker-compose run --rm --no-deps --name e2e-tests --entrypoint="pytest /tests/e2e -vv" tests

restart-db:
	-docker exec -it postgres psql -U postgres -c "SELECT pg_reload_conf();"

black:
	black -l 86 $$(find * -name '*.py')
