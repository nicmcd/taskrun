.SUFFIXES:
.PHONY: help install clean lint test benchmark count

help:
	@echo "options are: install clean lint test benchmark count"

install:
	python3 setup.py install --user

clean:
	rm -rf build dist taskrun.egg-info taskrun/*.pyc taskrun/__pycache__ test/*.pyc test/__pycache__
	$(MAKE) -C test/alloclots/ clean

lint:
	pylint -r n taskrun

test: test/alloclots/alloclots
	python3 -m unittest -v -f

test/alloclots/alloclots: test/alloclots/alloclots.cc
	$(MAKE) -C test/alloclots/

benchmark:
	python3 test/benchmark.py

count:
	@echo "taskrun/ - "$(shell echo taskrun/*.py | wc -w)" files"
	@wc taskrun/*.py | sort -n -k1
	@echo ""
	@echo "test/ - "$(shell echo test/*.py | wc -w)" files"
	@wc test/*.py | sort -n -k1
