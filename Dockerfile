FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY config.yaml .
RUN chmod +x ./entrypoint*

ENTRYPOINT ["./entrypoint.sh"]
