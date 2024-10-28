install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

test:
	python -m pytest -vv --cov=calculate_route test_*.py viz/test_*.py 

format:	
	black *.py viz/*.py 

lint:

	pylint --disable=R,C,protected-access --ignore-patterns=test_.*?py *.py\
		viz/*.py

container-lint:
	docker run --rm -i hadolint/hadolint < Dockerfile

refactor: format lint

deploy:
	#deploy goes here
		
all: install lint test format deploy