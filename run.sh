#!/bin/sh

virtualenv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

python site/manage.py migrate
python site/manage.py runserver
