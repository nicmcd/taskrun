.SUFFIXES:
.PHONY: help install clean lint test benchmark count

help:
	@echo "options are: install clean lint test benchmark count"

install:
	python3 setup.py install --user --record files.txt

uninstall:
	cat files.txt | xargs rm -rf

clean:
	rm -rf build dist taskrun.egg-info taskrun/*.pyc taskrun/__pycache__ test/*.pyc test/__pycache__
	$(MAKE) -C test/testprogs/ clean

lint:
	pylint -r n taskrun

test: test/testprogs/alloclots test/testprogs/burncycles
	python3 -m unittest -v -f

test/testprogs/alloclots: test/testprogs/alloclots.cc
	$(MAKE) -C test/testprogs/

test/testprogs/burncycles: test/testprogs/burncycles.cc
	$(MAKE) -C test/testprogs/

benchmark:
	python3 test/benchmark.py

count:
	@echo "taskrun/ - "$(shell echo taskrun/*.py | wc -w)" files"
	@wc taskrun/*.py | sort -n -k1
	@echo ""
	@echo "test/ - "$(shell echo test/*.py | wc -w)" files"
	@wc test/*.py | sort -n -k1
