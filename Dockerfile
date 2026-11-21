# syntax=docker/dockerfile:1.7.0
ARG SOURCE_DATE_EPOCH=0
ARG PYTHONHASHSEED=0
ARG PYTHON_IMAGE=python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b

FROM ${PYTHON_IMAGE} AS builder
ARG SOURCE_DATE_EPOCH
ARG PYTHONHASHSEED
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_CACHE_DIR=1
WORKDIR /build
COPY pyproject.toml MANIFEST.in README.md ./
COPY config ./config
COPY src ./src
COPY requirements/build.lock /tmp/build.lock
RUN python -m pip install --no-cache-dir --requirement /tmp/build.lock
RUN SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH}" PYTHONHASHSEED="${PYTHONHASHSEED}" python -m build --sdist --wheel --no-isolation --outdir /dist

FROM ${PYTHON_IMAGE} AS runtime
ARG SOURCE_DATE_EPOCH
ARG PYTHONHASHSEED
ARG ARCHON_SOURCE_SHA=unknown
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_CACHE_DIR=1 \
    ARCHON_STATE=/var/lib/archon ARCHON_WORKSPACE=/workspace ARCHON_SOURCE_SHA=${ARCHON_SOURCE_SHA}
RUN groupadd --system --gid 10001 archon \
    && useradd --system --uid 10001 --gid archon --home-dir /home/archon \
       --create-home --shell /usr/sbin/nologin archon \
    && install -d -m 0755 /etc/archon \
    && install -d -m 0700 -o archon -g archon /var/lib/archon /workspace
WORKDIR /app
COPY --from=builder /dist/*.whl /tmp/
COPY container/entrypoint.sh /usr/local/bin/archon-entrypoint
COPY requirements/runtime.lock /tmp/runtime.lock
RUN SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH}" PYTHONHASHSEED="${PYTHONHASHSEED}" python -m pip install --no-cache-dir --requirement /tmp/runtime.lock \
    && SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH}" PYTHONHASHSEED="${PYTHONHASHSEED}" python -m pip install --no-cache-dir --no-deps /tmp/jarvis_v2-0.0.3-py3-none-any.whl \
    && python -m pip check \
    && rm -f /tmp/jarvis_v2-0.0.3-py3-none-any.whl /tmp/runtime.lock \
    && chmod 0755 /usr/local/bin/archon-entrypoint
USER 10001:10001
ENV HOME=/home/archon
ENTRYPOINT ["/usr/local/bin/archon-entrypoint"]
CMD ["archon-native-controller", "--watch", "--repository", "/app"]
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD ["jarvis-v2", "health", "--state", "/var/lib/archon", "--repo", "/app"]
