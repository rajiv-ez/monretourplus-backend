#!/usr/bin/env bash

# Installer les dépendances (optionnel si géré par render.yaml)
pip install -r requirements.txt

# Appliquer les migrations
python manage.py migrate

# Collecter les fichiers statiques
python manage.py collectstatic --noinput
