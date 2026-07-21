PYTHON ?= python3

.PHONY: test build man clean

test:
	$(PYTHON) -m compileall -q pipes_sh.py tests
	$(PYTHON) -m unittest discover -s tests -v
	$(PYTHON) pipes_sh.py --self-test
	$(PYTHON) -O pipes_sh.py --self-test

build:
	$(PYTHON) -m build --wheel --no-isolation

man:
	groff -man -Tutf8 pipes.6 >/dev/null

clean:
	rm -rf build dist *.egg-info __pycache__ tests/__pycache__
