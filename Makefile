SHELL := /bin/bash
ROOT := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

.PHONY: nothing
nothing:

#@help: build the package
build:
	@echo "building picas..."
	@poetry build

#@help: cleanup the python build artifacts and uninstall picas if installed
clean-build:
	@echo "cleaning build artifacts..."
	@rm -rf picas.egg-info picasclient.egg-info build dist || true
	@python -m pip uninstall -y picas || true

#@help: install the package in the current python environment
install: clean-build
	@echo "installing picasclient..."
	@python -m pip install -v --force-reinstall --no-deps .
	@echo "Checking installed files..."
	@python -m pip show -f picas | grep -E "(Location|Files|Entry)" || true
	@echo "Checking for picas-cli executable..."
	@which picas-cli || echo "picas-cli not found in PATH"
	@ls -la $${VIRTUAL_ENV}/bin/picas* 2>/dev/null || echo "No picas scripts found in venv/bin"
	@echo "Python path check:"
	@python -c "import picas.apps.picas_cli; print('Module found:', picas.apps.picas_cli.__file__)"

#@help: uninstall the package from the current python environment
uninstall:
	@echo "uninstalling picasclient..."
	@python -m pip uninstall -y picas || true

#@help: run the tests
test:
	@echo "running tests..."
	@pytest tests

#@help: render the tutorial notebooks from the python scripts
#@help: the notebooks are generated in examples/notebooks
tutorial:
	@echo "running tutorial..."
	mkdir -p examples/notebooks
	@cd examples && jupytext --to ipynb 00-environment-setup.py --output notebooks/00-environment-setup.ipynb
	@cd examples && jupytext --to ipynb 01-database-setup.py --output notebooks/01-database-setup.ipynb
	@cd examples && jupytext --to ipynb 02-local-run.py --output notebooks/02-local-run.ipynb
	@cd examples && jupytext --to ipynb 03-spider-run.py --output notebooks/03-spider-run.ipynb
	@cd examples && jupytext --to ipynb 04-slurm-snellius.py --output notebooks/04-slurm-snellius.ipynb

#@help: clean the tutorial files
clean-tutorial:
	@echo "cleaning tutorial files..."
	@rm -fvr examples/*.ipynb
	@rm -fvr examples/*.out examples/*.err

#@help: pull the docker images
docker-compose-pull:
	@echo "pulling docker images..."
	@docker compose -f containers/docker/docker-compose.yml pull

#@help: start the docker-compose environment in detached mode
docker-compose-up:
	@echo "starting docker-compose..."
	@docker compose -f containers/docker/docker-compose.yml up -d

#@help: stop the docker-compose environment
docker-compose-down:
	@echo "stopping docker-compose..."
	@docker compose -f containers/docker/docker-compose.yml down

#@help: show the docker-compose logs
docker-compose-logs:
	@echo "showing docker-compose logs..."
	@docker compose -f containers/docker/docker-compose.yml logs --tail=100 --follow

#@help: restart the docker-compose environment
docker-compose-restart:
	@echo "restarting docker-compose..."
	@docker compose -f containers/docker/docker-compose.yml restart

#@help: clear the docker-compose containers, volumes, and networks
docker-compose-clear:
	@echo "clearing docker-compose containers..."
	@docker compose -f containers/docker/docker-compose.yml down --remove-orphans
	@docker volume prune -f
	@docker network prune -f
	@echo "Docker-compose containers cleared."

#@help: clean all build artifacts, tutorial files, and temporary files
clean: clean-build clean-tutorial
	@rm -fvr \#* *~ *.exe out build *.egg* dist
	@rm -fvr examples/*.out examples/*.err
	@find . -name __pycache__ -exec rm -fvr '{}' \;

#@help: clean, build the package, pull the docker image, render the tutorial notebooks
all: clean build docker-compose-pull tutorial


define AWK_SCRIPT
BEGIN {
	help = "";
}
/^#@help:/ {
	sub(/^#@help:[[:space:]]*/, "", $$0);
	help = help $$0;
}
/^[a-zA-Z0-9_.@%\/\-]+:/ {
	if (match($$0, /^([a-zA-Z0-9_.@%\/\-]+):/, var)) {
		printf "  %-30s %s\n", var[1], help;
	}
	help = "";
}
endef
export AWK_SCRIPT

#@help: show this help message
help:
	@echo "Available targets:"
	@awk "$$AWK_SCRIPT" $(MAKEFILE_LIST)
