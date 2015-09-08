.SUFFIXES:
.PHONY: help install clean lint test benchmark

help:
	@echo "options are: install clean lint test benchmark"

install:
	python3 setup.py install --user

clean:
	rm -rf build dist taskrun.egg-info taskrun/*.pyc taskrun/__pycache__ test/*.pyc test/__pycache__

lint:
	pylint -r n taskrun

test:
	python3 -m unittest -v -f

benchmark:
	python3 test/benchmark.py
