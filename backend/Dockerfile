FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install gunicorn==20.1.0 


RUN python -m pip install -r requirements.txt --no-cache-dir

COPY . .



CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram.wsgi"]