.PHONY: all setup run clean test lint db-up db-down db-migrate

VENV_NAME?=env
PYTHON=${VENV_NAME}/bin/python
PIP=${VENV_NAME}/bin/pip
APP_DIR=src/app
MODULE_PATH=src.app
REQUIREMENTS=requirements.txt
HOST=0.0.0.0
PORT=8080

all: setup

$(VENV_NAME)/bin/activate: $(REQUIREMENTS)
	test -d $(VENV_NAME) || python3 -m venv $(VENV_NAME)
	${PIP} install -r $(REQUIREMENTS)
	touch $(VENV_NAME)/bin/activate

setup: $(VENV_NAME)/bin/activate

run: setup
	$(PYTHON) -m uvicorn $(MODULE_PATH).main:app --host $(HOST) --port $(PORT) --reload

clean:
	rm -rf $(VENV_NAME)
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type d -name '__pycache__' -exec rm -rf {} +


### Database management

DB_CONTAINER_NAME=shortlink-postgres
DB_PASSWORD=password
DB_PORT=5432
DB_NAME=db

# Start PostgreSQL container using the official image
db-up:
	@if [ -z "$$(docker ps -q -f name=$(DB_CONTAINER_NAME))" ]; then \
		echo "Starting PostgreSQL container..."; \
		docker pull postgres:latest; \
		docker run --name $(DB_CONTAINER_NAME) -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=$(DB_PASSWORD) -e POSTGRES_DB=$(DB_NAME) -p $(DB_PORT):5432 -d postgres; \
		sleep 5; \
	else \
		echo "PostgreSQL container $(DB_CONTAINER_NAME) is already running."; \
	fi

# Stop and remove the PostgreSQL container
db-down:
	docker stop $(DB_CONTAINER_NAME) && docker rm $(DB_CONTAINER_NAME)

# Run Alembic migrations
db-migrate: db-up setup
	cd src && alembic upgrade head && cd ..


### Redis

REDIS_CONTAINER_NAME=shortlink-redis
REDIS_PORT=6379

# Start Redis container using the official image
redis-up:
	@if [ -z "$$(docker ps -q -f name=$(REDIS_CONTAINER_NAME))" ]; then \
		echo "Starting Redis container..."; \
		docker pull redis:latest; \
		docker run --name $(REDIS_CONTAINER_NAME) -p $(REDIS_PORT):6379 -d redis; \
		sleep 5; \
	else \
		echo "Redis container $(REDIS_CONTAINER_NAME) is already running."; \
	fi

# Stop and remove the Redis container
redis-down:
	docker stop $(REDIS_CONTAINER_NAME) && docker rm $(REDIS_CONTAINER_NAME)
