.PHONY: build docs install test

init: build lint test coverage

install:
	pip install -e .

build:
	pip install -e .[tests,docs]

lint:
	flake8 okami tests

test:
	py.test tests --verbose --capture=no

coverage:
	py.test tests --cov-config=.coveragerc --cov-report=term --cov=okami

documentation:
	cd docs && make html serve

publish:
	pip install wheel
	python setup.py bdist_wheel --universal upload
	rm -rf build dist .egg requests.egg-info
