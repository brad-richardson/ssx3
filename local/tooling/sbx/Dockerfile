# Sandbox image for untrusted-model opencode workers (Brad 09-26: free-model bake-off).
# = the ssx3 bradflix build image + opencode. The container is the security boundary:
# it sees only its own clone at /work, a tmpfs home, no host credentials, and reaches
# the internet only through the allowlisting proxy (see proxy/ and sbx_run.sh).
FROM ssx3-hs1
RUN apt-get update && apt-get install -y --no-install-recommends curl unzip && rm -rf /var/lib/apt/lists/*
ARG OPENCODE_VERSION=
RUN curl -fsSL https://opencode.ai/install -o /tmp/install && \
    HOME=/opt/oc bash /tmp/install ${OPENCODE_VERSION:+--version $OPENCODE_VERSION} && \
    ln -s /opt/oc/.opencode/bin/opencode /usr/local/bin/opencode && chmod -R a+rX /opt/oc && rm /tmp/install
