VENV_NAME = /tmp/flyin-venv
PYTHON = $(VENV_NAME)/bin/python
MAP ?= maps/easy/02_simple_fork.txt
 
install:
	python3 -m venv $(VENV_NAME)
	$(VENV_NAME)/bin/pip install -r requirements.txt
 
run:
	$(PYTHON) main.py $(MAP)
 
debug:
	$(PYTHON) -m pdb main.py $(MAP)
 
clean:
	rm -rf __pycache__ .mypy_cache
 
lint:
	$(VENV_NAME)/bin/flake8 .
	$(VENV_NAME)/bin/mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
 
lint-strict:
	$(VENV_NAME)/bin/flake8 .
	$(VENV_NAME)/bin/mypy . --strict
 