FROM python:3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 80
CMD [ "gunicorn", "app:app", "-b", ":80", "-w", "4" ]
