IMAGE := ponylang/library-documentation-action

all: build

build:
	docker build --pull -t "${IMAGE}:release" .
	docker build --pull -t "${IMAGE}:latest" .
	docker build --pull -t "ghcr.io/${IMAGE}:release" .
	docker build --pull -t "ghcr.io/${IMAGE}:latest" .

push: build
	docker push "${IMAGE}:release"
	docker push "${IMAGE}:latest"
	docker push "ghcr.io/${IMAGE}:release"
	docker push "ghcr.io/${IMAGE}:latest"

pylint: build
	docker run --entrypoint pylint --rm "ghcr.io/${IMAGE}:latest" /entrypoint.py

.PHONY: build pylint
