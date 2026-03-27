.PHONY: install clean test lint help

install:
	pip install -r requirements.txt
	pip install -e .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete
	rm -rf build/ dist/ *.egg-info/ models/ audio/

test:
	pytest tests/

lint:
	flake8 voxshell/

help:
	@echo "install - install dependencies"
	@echo "clean - remove build/cache files"
	@echo "test - run tests"
	@echo "lint - run linting"
