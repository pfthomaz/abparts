#!/bin/bash
docker compose cp check_images_in_db.py api:/tmp/check_images_in_db.py
docker compose exec api python /tmp/check_images_in_db.py
