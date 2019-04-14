SRC=$(HOME)/code/supercontest
VENV=$(SRC)/.venv
DB_CONTAINER=database
DB_USER=supercontest
DB_NAME=supercontest
DB_DUMP=$(SRC)/backups/postgres/supercontest.dump

# Starting docker containers.

.PHONY: start-dev
start-dev:
	docker-compose up -d app_dev

.PHONY: build-start-dev
build-start-dev:
	docker-compose up -d --build app_dev

.PHONY: start-prod
start-prod:
	docker-compose up -d web_server certbot

.PHONY: build-start-prod
build-start-prod:
	docker-compose up -d --build web_server certbot

# This requires an existing container named postgres with a user named
# supercontest and a database named supercontest.
.PHONY: explore-db
explore-db:
	docker-compose exec $(DB_CONTAINER) psql -U $(DB_USER) -d $(DB_NAME)

# Backup requires our db container to already be running.
.PHONY: backup-db
backup-db:
	docker-compose exec -T $(DB_CONTAINER) \
		pg_dump --clean --format=c -U $(DB_USER) -d $(DB_NAME) > $(DB_DUMP)

# Restore is intentionally forceful, dropping before recreating. Because of the
# DROP command, no connections to the supercontest db can be open. This means
# two things: (1) we connect to another db instead (postgres) and (2) we kill the
# flask container, which is connected to the db. You'll have to
# docker-compose up/start the desired services after this runs.
.PHONY: restore-db
restore-db:
	docker-compose stop
	docker-compose up -d $(DB_CONTAINER)
	echo waiting for postgres 5432 to be ready
	sleep 2
	docker-compose exec -T $(DB_CONTAINER) \
		pg_restore --clean --create -U $(DB_USER) -d postgres < $(DB_DUMP)
	docker-compose stop $(DB_CONTAINER)

# Intentionally phony so it regenerates.
.PHONY: virtualenv
virtualenv:
	virtualenv $(VENV) --python=python3.7 --clear --always-copy
	$(VENV)/bin/pip install -e $(SRC)

.PHONY: reindex-ctags
reindex-ctags: virtualenv
	ctags --python-kinds=-iv -R -o ~/.tags \
		`$(VENV)/bin/python -c "import os, sys; print(' '.join('{}'.format(d) for d in sys.path if os.path.isdir(d)))")`

