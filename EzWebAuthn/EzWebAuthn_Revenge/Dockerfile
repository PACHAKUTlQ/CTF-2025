FROM python:3.12-slim

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT [ "bash", "-c", "(python3 db.py init && gunicorn -w 8 -b 0.0.0.0:80 app:app) & python3 task.py" ]