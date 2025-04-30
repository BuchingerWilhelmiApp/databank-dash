FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app/src

RUN apt-get update && apt-get install -y build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# now copy your Python code into the WORKDIR
COPY src/ .

EXPOSE 8060

CMD ["python", "-u", "app.py"]
