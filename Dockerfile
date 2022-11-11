FROM ponylang/ponyc:release-alpine

RUN apk add --update --no-cache \
  bash \
  libffi \
  libffi-dev \
  libressl \
  libressl-dev \
  make \
  python3 \
  python3-dev \
  py3-pip \
  tar

RUN pip3 install --upgrade pip \
  gitpython \
  in_place \
  mkdocs \
  mkdocs-material \
  pylint \
  pyyaml

COPY entrypoint.py /entrypoint.py

ENTRYPOINT ["/entrypoint.py"]
