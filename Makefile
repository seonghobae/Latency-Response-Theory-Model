.PHONY: install test example

install:
	python -m pip install -e ".[dev]"

test:
	python -m unittest discover -s validation -p 'test_*.py' -v

example:
	python examples/fit_synthetic.py
