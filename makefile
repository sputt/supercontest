SRC=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
VENV=$(SRC)/.venv
APP_DEV_CONTAINER=supercontest-app-dev
APP_PROD_CONTAINER=supercontest-app-prod
DB_CONTAINER=supercontest-database
DB_USER=supercontest
DB_NAME=supercontest
DB_DUMP=$(SRC)/backups/postgres/supercontest.dump

# Starting docker containers.

.PHONY: start-dev
start-dev:
	docker-compose up -d supercontest-app-dev

.PHONY: build-start-dev
build-start-dev:
	docker-compose up -d --build supercontest-app-dev

.PHONY: start-prod
start-prod:
	docker-compose up -d supercontest-app-prod

.PHONY: build-start-prod
build-start-prod:
	docker-compose up -d --build supercontest-app-prod

# This requires an existing container named postgres with a user named
# supercontest and a database named supercontest.
.PHONY: explore-local-db
explore-local-db:
	docker-compose exec $(DB_CONTAINER) psql -U $(DB_USER) -d $(DB_NAME)

# This requires an existing container running the dev app. It enters a
# python context with access to the db via sqlalchemy to test queries.
.PHONY: shell
shell:
	docker-compose exec $(APP_DEV_CONTAINER) python manage.py shell

# These require an existing container running the dev/prod app. They
# simply shell in so you can run stuff like `python manage.py db`.
.PHONY: enter-dev-app
enter-dev-app:
	docker-compose exec $(APP_DEV_CONTAINER) bash
.PHONY: enter-prod-app
enter-prod-app:
	docker-compose exec $(APP_PROD_CONTAINER) bash

# Backup requires our db container to already be running.
.PHONY: backup-local-db-to-local
backup-local-db-to-local:
	docker-compose exec -T $(DB_CONTAINER) \
		pg_dump --clean --format=c -U $(DB_USER) -d $(DB_NAME) > $(DB_DUMP)

# Restore is intentionally forceful, dropping before recreating. Because of the
# DROP command, no connections to the supercontest db can be open. This means
# two things: (1) we connect to another db instead (postgres) and (2) we kill the
# flask container, which is connected to the db. You'll have to
# docker-compose up/start the desired services after this runs.
.PHONY: restore-local-db-from-local
restore-local-db-from-local:
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
	$(VENV)/bin/python -m pip install req-compile
	$(VENV)/bin/python -m pip install -e $(SRC) -c compiled-requirements.txt

.PHONY: reindex-ctags
reindex-ctags: virtualenv
	ctags --python-kinds=-iv -R -o ~/.tags \
		`$(VENV)/bin/python -c "import os, sys; print(' '.join('{}'.format(d) for d in sys.path if os.path.isdir(d)))")`

.PHONY: deploy
deploy:
	ANSIBLE_CONFIG=~/code/supercontest/ansible/ansible.cfg ansible-playbook -i ansible/hosts ansible/deploy.yml --key-file "~/.ssh/digitalocean"

# Basically wraps the local backup with an ssh/scp session.
.PHONY: backup-remote-db-to-local
backup-remote-db-to-local:
	ANSIBLE_CONFIG=~/code/supercontest/ansible/ansible.cfg ansible-playbook -i ansible/hosts ansible/backup.yml --key-file "~/.ssh/digitalocean"

# Basically wraps the local restore with an ssh/scp session.
.PHONY: restore-remote-db-from-local
restore-remote-db-from-local:
	ANSIBLE_CONFIG=~/code/supercontest/ansible/ansible.cfg ansible-playbook -i ansible/hosts ansible/restore.yml --key-file "~/.ssh/digitalocean"

# Generate a constraints file from the input requirements
compiled-requirements.txt: requirements.txt test-requirements.txt
	req-compile --solution compiled-requirements.txt requirements.txt test-requirements.txt > compiled-requirements.txt.tmp
	mv compiled-requirements.txt.tmp compiled-requirements.txt

# Fetch all new versions from PyPI
.PHONY: update-requirements
update-requirements: | clear-requirements compiled-requirements.txt

.PHONY: clear-requirements
clear-requirements:
	rm compiled-requirements.txt

.PHONY: test-python
test-python: update-requirements
	tox

.PHONY: test-js
test-js:
	rm -rf ./.jsenv ./node_modules && virtualenv .jsenv --python=python3.7 --always-copy
	. ./.jsenv/bin/activate && pip install nodeenv jasmine && nodeenv -p && npm install eslint
	./node_modules/.bin/eslint supercontest/static/js/
	# ./.jsenv/bin/jasmine ci --browser chrome --config tests/js/jasmine.yml

.PHONY: test
test: test-python test-js
