FROM python:3.9

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash python

USER python

ENV PATH="/home/python/.local/bin:${PATH}"

WORKDIR /home/python

RUN git clone https://github.com/ggerganov/whisper.cpp.git -b v1.4.0 \
    && cd whisper.cpp \
    && ./models/download-ggml-model.sh medium.en \
    && make main \
    && make quantize \
    && ./quantize models/ggml-medium.en.bin models/ggml-medium.en-q5_0.bin q5_0

RUN pip upgrade --no-cache-dir pip

COPY --chown=python requirements.txt /home/python/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=python agent.py main.py /home/python/

EXPOSE 5000
ENTRYPOINT [ "uvicorn", "main:app", "--port", "5000" ]