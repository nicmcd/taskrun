.SUFFIXES:
.PHONY: help install clean lint test

help:
	@echo "options are: install clean lint test"

install:
	python3 setup.py install --user

clean:
	rm -rf build dist taskrun.egg-info taskrun/*.pyc taskrun/__pycache__ test/*.pyc test/__pycache__

lint:
	pylint -r n taskrun

test:
	python3 -m unittest -v -f
