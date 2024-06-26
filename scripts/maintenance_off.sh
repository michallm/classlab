#!/bin/bash

docker compose -f docker-compose.prod.yml exec django python manage.py maintenance_mode off
