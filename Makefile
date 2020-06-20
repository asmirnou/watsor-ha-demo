venv:
	python3.7 -m venv venvha venvad
	venvha/bin/python -m pip install --upgrade pip setuptools
	venvad/bin/python -m pip install --upgrade pip setuptools

install:
	venvha/bin/python -m pip install --upgrade homeassistant
	venvad/bin/python -m pip install --upgrade appdaemon

runha:
	venvha/bin/hass --config config --log-file logs/home-assistant.log --open-ui

runad:
	venvad/bin/appdaemon --config config
