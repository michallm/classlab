#!/bin/bash
# This script updates the local repository with the latest changes from the remote repository
# and restart the following container django, celerybeat, flower, celeryworker

git pull
docker compose -f docker-compose.prod.yml up -d --build --no-deps django celerybeat flower celeryworker
echo "Done!"
