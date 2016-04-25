install:
	pip install -r requirements_dev.txt
	pip install -r requirements.txt

lint:
	flake8 feedback --ignore=F821,E123,W292,W391,E731

run:
	python app.py

unit:
	nosetests --logging-level=ERROR
