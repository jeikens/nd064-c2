FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 50051

COPY . /app

CMD ["python", "main.py"]