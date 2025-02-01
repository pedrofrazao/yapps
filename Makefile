# Variables
PYTHON = python3
PYTESTFILE = ppSlib/run_all_tests.py

test: 
	@$(PYTHON) ${PYTESTFILE}

clean:
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' -delete