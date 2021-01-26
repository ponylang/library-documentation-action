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
  py3-pip

RUN pip3 install --upgrade pip \
  wheel \
  gitpython \
  in_place \
  mkdocs \
  mkdocs-ponylang \
  pylint \
  pyyaml

COPY entrypoint.py /entrypoint.py

ENTRYPOINT ["/entrypoint.py"]
