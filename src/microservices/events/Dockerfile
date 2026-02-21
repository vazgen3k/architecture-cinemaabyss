FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# (опционально) чтобы собрать некоторые зависимости быстрее/надёжнее
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# код
COPY . .

# порт берём из env PORT (в compose у тебя PORT=8082)
CMD ["sh", "-c", "uvicorn serve:app --host 0.0.0.0 --port ${PORT:-8082}"]