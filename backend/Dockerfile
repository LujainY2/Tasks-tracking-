FROM python:3.12-slim AS builder
WORKDIR /app

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

COPY src /app/src

FROM python:3.12-slim AS runner
WORKDIR /app

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

COPY --from=builder /app/src /app/src
ENV PYTHONPATH=/app/src

EXPOSE 8000
CMD ["uvicorn", "mysite.main:app", "--host", "0.0.0.0", "--port", "8000"]