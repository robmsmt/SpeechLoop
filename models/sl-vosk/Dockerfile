FROM alphacep/kaldi-vosk-server:latest

EXPOSE 2700
ENV VOSK_SAMPLE_RATE=16000
ENV MODEL_VERSION 0.15
RUN mkdir /opt/vosk-model-en \
   && cd /opt/vosk-model-en \
   && wget -q http://alphacephei.com/vosk/models/vosk-model-small-en-us-${MODEL_VERSION}.zip \
   && unzip vosk-model-small-en-us-${MODEL_VERSION}.zip \
   && mv vosk-model-small-en-us-${MODEL_VERSION} model \
   && rm -rf vosk-model-small-en-us-${MODEL_VERSION}.zip

RUN wget -q https://github.com/vi/websocat/releases/download/v1.8.0/websocat_1.8.0_newer_amd64.deb \
    && dpkg -i websocat_1.8.0_newer_amd64.deb

HEALTHCHECK  --interval=10s --timeout=5s \
  CMD websocat -uU ws://localhost:2700  || exit 1

WORKDIR /opt/vosk-server/websocket
CMD [ "python3", "./asr_server.py", "/opt/vosk-model-en/model" ]
