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

integration-tests: up restart-db
	docker-compose run --rm --no-deps --name integration_tests --entrypoint="pytest /tests/integration -vv" tests

e2e-tests: up restart-db
	docker-compose run --rm --no-deps --name e2e-tests --entrypoint="pytest /tests/e2e -vv" tests

restart-db:
	-docker exec -it architecture-patterns-db psql -d warehouse -U allocation -c "drop table allocation; drop table batch; drop table order_line; drop table product; drop table allocations_view;"

black:
	black -l 86 $$(find * -name '*.py')
