# Some simple testing tasks (sorry, UNIX only).

FLAGS=
SCALA_VERSION?=2.11
KAFKA_VERSION?=0.9.0.1
DOCKER_IMAGE_NAME=pygo/kafka:$(SCALA_VERSION)_$(KAFKA_VERSION)

flake:
	flake8 aiokafka tests

test: flake
	@DOCKER_IMAGE_NAME=$(DOCKER_IMAGE_NAME) FLAGS=$(FLAGS) sh runtests.sh

vtest: flake
	@DOCKER_IMAGE_NAME=$(DOCKER_IMAGE_NAME) FLAGS="-v $(FLAGS)" sh runtests.sh

cov cover coverage:
	@DOCKER_IMAGE_NAME=$(DOCKER_IMAGE_NAME) FLAGS="--cov aiokafka --cov-report html $(FLAGS)" sh runtests.sh
	@echo "open file://`pwd`/htmlcov/index.html"

clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -f `find . -type f -name '@*' `
	rm -f `find . -type f -name '#*#' `
	rm -f `find . -type f -name '*.orig' `
	rm -f `find . -type f -name '*.rej' `
	rm -f .coverage
	rm -rf htmlcov
	rm -rf build
	rm -rf cover
	rm -rf dist
	@docker rmi -f $(DOCKER_IMAGE_NAME) || true

doc:
	make -C docs html
	@echo "open file://`pwd`/docs/_build/html/index.html"

.PHONY: all flake test vtest cov clean doc
