# Llama.cpp with Turbo Quant and MTP image plus an api app to restart llama-server with
# select parameters without the need to restart the container.
# 
# Utilises an intermediate build image from https://github.com/SimonLea-sg/llama-tq-docker-build/
# To save rebuilding the llama.cpp portion of the image for multiple apps.

# Choose which image to use 
# (visit https://github.com/SimonLea-sg/llama-tq-docker-build/ for image build instructions)

# llamacpp-tq-mtp-base-all = Full llama.cpp toolset.
# llamacpp-tq-mtp-base-all = llama.cpp llama-server and webgui only.

FROM llamacpp-tq-mtp-base-all
# FROM llamacpp-tq-mtp-base-all

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

COPY api/requirements.txt /tmp/requirements.txt

RUN python3 -m venv .venv \
    && . .venv/bin/activate \
    && python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip3 install --no-cache-dir -r /tmp/requirements.txt
   
RUN rm /tmp/requirements.txt

COPY api/ /app/api/
COPY docker/.env /app/api/.env

RUN mkdir -p /models

COPY ./docker/entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000 8080

HEALTHCHECK --interval=10s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -fsS http://localhost:8000/health >/dev/null || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]