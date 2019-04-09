FROM postgres:latest

# This image expects a database to already exist in the docker-compose volume.
# You can uncomment the below section to restore a backup (or do it manually).

# The official Postgres image will execute any sql found in this directory,
# which means it will recreate the database in the dump file.
# COPY ./backups/postgres/dump.sql /docker-entrypoint-initdb.d/
