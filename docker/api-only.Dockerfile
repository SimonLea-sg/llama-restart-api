# Llama.cpp with Turbo Quant and MTP image plus an api app to restart llama-server with
# select parameters without the need to restart the container.

# Choose which image to use 
# (visit https://github.com/SimonLea-sg/llama-tq-docker-build/ for image build instructions)

# llamacpp-tq-mtp-base-all    = Full llama.cpp toolset.
# llamacpp-tq-mtp-base-server = llama.cpp llama-server and webgui only.

# FROM llamacpp-tq-mtp-base-all
FROM llamacpp-tq-server as server

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install Python
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Copy files
COPY api/ docker/.env ./docker/entrypoint.sh /app/api/
COPY ./docker/entrypoint.sh /app/

# Setup Python
RUN python3 -m venv .venv \
    && . .venv/bin/activate \
    && python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip3 install --no-cache-dir -r /app/api/requirements.txt \
    && rm /app/api/requirements.txt

# Final settings
RUN mkdir -p /models \
    && chmod +x /app/entrypoint.sh

EXPOSE 8000 8080

HEALTHCHECK --interval=3600s --timeout=5s --start-period=20s --retries=3 \
  CMD bash -c 'curl -fsS http://localhost:8000/health && pgrep -x llama-server > /dev/null || exit 1'

ENTRYPOINT ["/app/entrypoint.sh"]


FROM llamacpp-tq-full as full

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install Python
RUN apt-get update && \
    rm -rf /var/lib/apt/lists/*

# Copy files
COPY api/ docker/.env ./docker/entrypoint.sh /app/api/
COPY ./docker/entrypoint.sh /app/

# Setup Python
RUN . .venv/bin/activate \
    && pip3 install --no-cache-dir -r /app/api/requirements.txt \
    && rm /app/api/requirements.txt

# Final settings
RUN mkdir -p /models \
    && chmod +x /app/entrypoint.sh

EXPOSE 8000 8080

HEALTHCHECK --interval=3600s --timeout=5s --start-period=20s --retries=3 \
  CMD bash -c 'curl -fsS http://localhost:8000/health && pgrep -x llama-server > /dev/null || exit 1'

ENTRYPOINT ["/app/entrypoint.sh"]

