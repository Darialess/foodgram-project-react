FROM python:3.8.6-slim

WORKDIR /app

COPY requirements.txt .

RUN apt update && \
    apt upgrade -y && \
    python3 -m pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "foodgram.wsgi", "-w", "4", "-t", "600", "-b", "0.0.0.0:8000"]