FROM ubuntu:20.04

RUN apt update && apt-get install -y libsndfile1 curl python3-dev python3-pip \
    && pip install fastapi uvicorn stt soundfile \
    && rm -rf /var/lib/apt/lists/*


EXPOSE 3200
COPY app /app
WORKDIR /app

RUN curl -L -o /app/coqui-stt-0.9.3-models.pbmm https://github.com/coqui-ai/STT/releases/download/v0.9.3/coqui-stt-0.9.3-models.pbmm
#RUN curl -o app https://github.com/coqui-ai/STT/releases/download/v0.9.3/coqui-stt-0.9.3-models.scorer

HEALTHCHECK  --interval=30s --timeout=5s --start-period=15s \
  CMD curl --fail http://localhost:3200/healthcheck  || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3200"]

# docker build -f Dockerfile . -t robmsmt/sl-coqui
# docker run -d --restart unless-stopped -p 3200:3200 robmsmt/sl-coqui-en-16k:latest
# docker run -it -p 3200:3200 robmsmt/sl-coqui
#docker run -it -p 3200:3200 robmsmt/sl-coqui-en-16k:latest
#docker commit <container_id> my-broken-container && docker run -it my-broken-container /bin/bash
