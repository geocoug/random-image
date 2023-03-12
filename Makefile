VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
TEST = pytest

# Dont show in help
# Create and activate a virtual environment
$(VENV)/bin/activate: requirements.txt
	python3 -m venv .venv
	$(PIP) install -U pip
	$(PIP) install -r requirements.txt

## Run the app
run:
	$(PYTHON) random_image.py -v tracker.json ./images/

## Remove temporary files
clean:
	rm -rf .ipynb_checkpoints
	rm -rf **/.ipynb_checkpoints
	rm -rf __pycache__
	rm -rf **/__pycache__
	rm -rf **/**/__pycache__
	rm -rf .pytest_cache
	rm -rf **/.pytest_cache
	rm -rf .ruff_cache
	rm -rf .coverage
	rm -rf build
	rm -rf dist
	rm -rf images

## Update pip and pre-commit
update: $(VENV)/bin/activate
	$(PIP) install -U pip
	$(PYTHON) -m pre_commit autoupdate

## Run pre-commit hooks
lint: $(VENV)/bin/activate
	$(PYTHON) -m pre_commit install --install-hooks
	$(PYTHON) -m pre_commit run --all-files

#################################################################################
# Self Documenting Commands                                                     #
# Source: https://gist.github.com/klmr/575726c7e05d8780505a                     #
#################################################################################
.DEFAULT_GOAL := help
.PHONY: help
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) == Darwin && echo '--no-init --raw-control-chars')
