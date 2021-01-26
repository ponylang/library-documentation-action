TAG := docker.pkg.github.com/ponylang/library-documentation-action/library-documentation:latest

all: build

build:
	docker build --pull -t ${TAG} .

pylint: build
	docker run --entrypoint pylint --rm ${TAG} /entrypoint.py

script: build
	docker run --entrypoint python3 --rm ${TAG} /entrypoint.py

.PHONY: build pylint
