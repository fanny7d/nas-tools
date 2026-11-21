FROM 0xforee/nas-tools@sha256:7fe01ad75f355375f47689e71f0436edf8e66964ad711e1c078e3dd104966650
ARG SOURCE_REVISION
LABEL org.opencontainers.image.source="https://github.com/fanny7d/nas-tools" \
      org.opencontainers.image.revision="${SOURCE_REVISION}"
RUN rm -rf /nas-tools && mkdir /nas-tools
COPY source/ /nas-tools/
COPY wheels/ /fork-wheels/
RUN python3 -m pip install --no-index --no-deps /fork-wheels/*.whl && \
    python3 -m pip show qbittorrent-api Flask-Cors bencode.py >/dev/null && \
    test -z "$(find /nas-tools -name '._*' -print -quit)" && \
    python3 -m compileall -q /nas-tools/app /nas-tools/scripts
ENV REPO_URL=https://github.com/fanny7d/nas-tools.git \
    NASTOOL_AUTO_UPDATE=false
