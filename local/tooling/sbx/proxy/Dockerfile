FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends tinyproxy && rm -rf /var/lib/apt/lists/*
COPY tinyproxy.conf /etc/tinyproxy/tinyproxy.conf
COPY allow.txt /etc/tinyproxy/allow.txt
USER nobody
CMD ["tinyproxy", "-d", "-c", "/etc/tinyproxy/tinyproxy.conf"]
