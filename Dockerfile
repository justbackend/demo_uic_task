# FROM python:3.13-slim
#
# WORKDIR /app
#
# COPY pyproject.toml poetry.lock* requirements.txt* ./
# RUN pip install --no-cache-dir -r requirements.txt
#
# COPY . .
#
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


FROM python:3.13-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]