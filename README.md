# Tasklist demo

Sample JSON API with django and a _rest-framework_ make-shift

# Install

```bash
# clone the repo...
# make a virtual env, (e.g.)
python3 -m venv env
# source it, and install packages

source env/bin/activate
pip install -r requirements.txt

# go to src folder, migrate and run.
cd src/
python manage.py migrate

# test it with
python manage.py test

python manage.py runserver
# or in production
# PY_DEBUG=0 PY_HOST=localhost gunicorn tasklist.wsgi -b 127.0.0.1:8000
```