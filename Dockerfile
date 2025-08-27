FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --upgrade pip && \
    pip cache purge && \
    python -m pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]