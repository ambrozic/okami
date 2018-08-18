.PHONY: init install build lint test coverage docs publish
.SILENT: init install build lint test coverage docs publish

init: build lint test coverage

install:
	pip install --upgrade pip setuptools wheel && pip install .

build:
	pip install --upgrade pip setuptools wheel && pip install -e .[tests,docs]

lint:
	flake8 okami tests

test:
	py.test tests --verbose --capture=no

coverage:
	py.test --cov-report=term --cov=okami tests

docs:
	mkdocs serve

publish:
	pip install wheel twine
	python setup.py sdist bdist_wheel --universal
	twine upload dist/*
	rm -rf build dist okami.egg-info
