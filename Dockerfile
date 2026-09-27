FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ai-chat-bot/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY shared /app/shared
COPY ai-chat-bot /app/ai-chat-bot

WORKDIR /app/ai-chat-bot

ENV PYTHONPATH="/app"

CMD ["python", "main.py"]
