# Stage 1: Build
FROM python:3.11-slim AS builder
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libgomp1 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt gunicorn gevent

# Stage 2: Production
FROM python:3.11-slim AS production
LABEL maintainer="PaySentinel" version="2.0.0"
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PORT=5000 \
    WORKERS=2 WORKER_CLASS=gevent LOG_LEVEL=info
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 curl tini \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 paysentinel
COPY --from=builder /root/.local /home/paysentinel/.local
ENV PATH=/home/paysentinel/.local/bin:$PATH
COPY --chown=paysentinel:paysentinel . .
RUN mkdir -p /app/models /app/logs /app/data /app/static \
    && chown -R paysentinel:paysentinel /app
USER paysentinel
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:$PORT/api/health || exit 1
EXPOSE 5000
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["sh", "-c", "exec gunicorn src.app:app --chdir /app --bind 0.0.0.0:$PORT --workers $WORKERS --worker-class $WORKER_CLASS --max-requests 1000 --max-requests-jitter 100 --log-level $LOG_LEVEL --access-logfile /app/logs/access.log --error-logfile /app/logs/error.log --timeout 120"]
