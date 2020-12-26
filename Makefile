test: python/*.py
	. ./python/test/py.sh -m pytest -vv -s python/test

install: *
	PROJECT_PATH=$(pwd) python/setup_pip.sh
	PROJECT_PATH=$(pwd) python/install.sh