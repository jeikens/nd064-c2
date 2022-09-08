FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 8080

COPY . /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port" , "8080"]