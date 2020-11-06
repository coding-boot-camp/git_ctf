# Welcome!
This is the back-end application for [OperationCode](https://operationcode.org) frozen in time. We have lovingly borrowed this repo for our git ctf challenge under it's MIT License.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Below are some of the original instructions for setting up dependencies.

- python@3.7 or greater (in some environments, you may need to specify version of python i.e. python test.py vs python3 test.py))
- git@2.17.1 or greater
- poetry@0.12.11 or greater

```bash
# Install dependencies (ensure poetry is already installed)
# if you are encountering an error with psycopg2 during poetry installation, ensure postgreqsql is installed (macOS: brew install postgresql)
poetry install

# Create database
# By default this creates a local sqlite database and adds tables for each of the defined models
# see example.env for database configurations
poetry run python src/manage.py migrate

# Create a superuser to add to the new database
poetry run python src/manage.py createsuperuser 

# Run local development
poetry run python src/manage.py runserver

# Run testing suite
poetry run pytest

# Run formatting and linting
poetry run black .
# the next line shouldn't output anything to the terminal if it passes
poetry run flake8
poetry run isort -rc .
```

## Running [Bandit](https://github.com/PyCQA/bandit)
Bandit is a tool designed to find common security issues in Python code. 

From within the `back-end/` directory you can run the following Bandit command: 

- `bandit -r .` runs all bandit tests recursively with only filters defined in the `.bandit` file.
