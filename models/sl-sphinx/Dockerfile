FROM python:3.9-slim-buster


RUN apt update && apt-get install -y curl libsndfile1 libpulse-dev \
    && rm -rf /var/lib/apt/lists/*

RUN buildDeps='gcc swig libasound2-dev ' \
    && apt-get update \
    && apt-get install -y $buildDeps --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && pip install soundfile fastapi uvicorn pocketsphinx numpy \
    && apt-get purge -y --auto-remove $buildDeps \
    && apt-get autoremove -y

EXPOSE 3000

COPY app /app

HEALTHCHECK  --interval=30s --timeout=5s --start-period=15s \
  CMD curl --fail http://localhost:3000/healthcheck  || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]

#docker build -f Dockerfile . -t robmsmt/bab-sphinx
#docker run -d --restart unless-stopped -p 3000:3000 robmsmt/bab-sphinx
