
.DEFAULT_GOAL := test

.PHONY: docker-build
docker-build:
	docker build -t semver-python:latest .

.PHONY: docs
docs:
	docker run -it --rm -v $(shell pwd):/app semver-python:latest sphinx-apidoc -F -o docs/source semver/
	docker run -it --rm -v $(shell pwd):/app semver-python:latest sphinx-build docs/source docs/target

.PHONY: test
test:
	docker run -it --rm -v $(shell pwd):/app:ro semver-python:latest python -m unittest discover -s test

