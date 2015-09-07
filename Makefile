.SUFFIXES:
.PHONY: help install lint test 

help:
	@echo "options are: install lint test"

install:
	python3 setup.py install --user

lint:
	pylint -r n taskrun

test:
	python3 -m unittest -v -f
