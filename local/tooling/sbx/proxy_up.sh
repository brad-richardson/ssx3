#!/bin/bash
# Start the allowlisting proxy: on sbx-int (internal, no route out) + the default bridge (its only way out).
docker network inspect sbx-int >/dev/null 2>&1 || docker network create --internal sbx-int >/dev/null
docker rm -f sbx-proxy >/dev/null 2>&1
docker run -d --name sbx-proxy --restart unless-stopped --network sbx-int --cap-drop ALL \
  --security-opt no-new-privileges --memory 256m ssx3-sbx-proxy >/dev/null
docker network connect bridge sbx-proxy
echo "sbx-proxy up"
