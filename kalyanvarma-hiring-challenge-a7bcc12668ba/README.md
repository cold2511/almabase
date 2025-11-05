# Spam Contacts
Spam-contacts demonstrates a secure REST API design. 
It explores functionalities like user management, spam marking, and searchable contact details, ideal for building spam identification and people search features.

# Tech Stack
Django, PostgreSQL


# How to build project?

Create virtual environment

```shell (Need to do during setup only)
python -m venv venv
```

Active virtual environment

```shell
source venv/bin/activate
```

Install packages

```shell (Need to do during setup only)
pip install -r app/requirements.txt
```

Setup database (Need to do during setup only)

```shell
python app/manage.py migrate
```

Run dev backend server

```shell
python app/manage.py runserver
```

The django app will run on http://localhost:8000

[Optional] Populate Database with test data

```shell
python app/manage.py populate
```

