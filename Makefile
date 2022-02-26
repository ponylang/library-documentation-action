IMAGE := ponylang/library-documentation-action

all: build

build:
	docker build --pull -t "${IMAGE}:release" .
	docker build --pull -t "${IMAGE}:latest" .

push: build
	docker push "${IMAGE}:release"
	docker push "${IMAGE}:latest"

pylint: build
	docker run --entrypoint pylint --rm "${IMAGE}:latest" /entrypoint.py

.PHONY: build pylint
