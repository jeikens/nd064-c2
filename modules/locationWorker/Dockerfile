FROM python:3.10

WORKDIR /app

#RUN apt-get install gcc musl-dev linux-headers geos libc-dev postgresql-dev

COPY requirements.txt /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . /app

CMD ["python", "main.py"]