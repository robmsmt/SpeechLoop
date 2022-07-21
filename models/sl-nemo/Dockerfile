FROM python:3.9-slim

ENV TZ=Europe/London
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ENV MODELNAME='stt_en_contextnet_1024.nemo'
ENV MODELTYPE='EncDecRNNTBPEModel'
ENV MODELURL='https://api.ngc.nvidia.com/v2/models/nvidia/nemo/stt_en_contextnet_1024/versions/1.9.0/files/stt_en_contextnet_1024.nemo'

EXPOSE 3500
COPY app /app
WORKDIR /app

RUN apt update && apt-get install -y gcc curl python3-dev python3-pip ffmpeg \
    && pip install numpy==1.22.4 fastapi uvicorn Cython torch==1.9.0+cpu torchvision==0.10.0+cpu torchaudio==0.9.0 -f https://download.pytorch.org/whl/torch_stable.html \
    && pip install nemo_toolkit[asr] \
    && curl -L -o /app/$MODELNAME $MODELURL \
    && rm -rf /var/lib/apt/lists/* \
    && apt remove -y gcc curl \
    && apt autoremove -y

HEALTHCHECK  --interval=30s --timeout=5s --start-period=15s \
  CMD curl --fail http://localhost:3500/healthcheck  || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3500"]

# docker build -f Dockerfile . -t robmsmt/sl-coqui
# docker run -d --restart unless-stopped -p 3200:3200 robmsmt/sl-coqui-en-16k:latest
# docker run -it -p 3200:3200 robmsmt/sl-coqui
#docker run -it -p 3200:3200 robmsmt/sl-coqui-en-16k:latest
#docker commit <container_id> my-broken-container && docker run -it my-broken-container /bin/bash
