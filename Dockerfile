FROM ponylang/ponyc:release-alpine

RUN apk add --update --no-cache \
  bash \
  git \
  git-fast-import \
  jq \
  libffi \
  libffi-dev \
  libressl \
  libressl-dev \
  make \
  python3 \
  python3-dev \
  py3-pip \
  && pip3 install --upgrade pip \
  && pip3 install wheel \
  && pip3 install mkdocs \
  && pip3 install mkdocs-ponylang

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
