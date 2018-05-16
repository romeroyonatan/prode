DOCKER := docker-compose -f local.yml
RUN_IN_DOCKER :=  $(DOCKER) run --rm django

dev:
	$(DOCKER) up

node:
	npm run dev

test:
	pytest

coverage:
	coverage run --source bp -m pytest

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint: ## check style with flake8
	flake8 bp

docker-build:  ## (re)build docker images (use after change requirements.txt file)
	$(DOCKER) build

docker-shell:
	$(RUN_IN_DOCKER) sh

docker-run:  # run command in ARGS variable in docker runtime
	$(RUN_IN_DOCKER) $(ARGS)

docker-test:
	$(RUN_IN_DOCKER) pytest

docker-django-shell:
	$(RUN_IN_DOCKER) python manage.py shell

docker-db-shell:
	$(RUN_IN_DOCKER) python manage.py dbshell
