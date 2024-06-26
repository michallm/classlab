#!/bin/bash

export $(grep -v '^#' .env | xargs)

docker compose -f docker-compose.prod.yml exec -it postgres sh -c "PGPASSWORD=$POSTGRES_PASSWORD psql -U $POSTGRES_USER $POSTGRES_DB"
