setup:
	python -m pip install -r backend/requirements.txt
	npm --prefix frontend install

test:
	python -m pytest backend/tests
	npm --prefix frontend test

build:
	npm --prefix frontend run build

run:
	uvicorn app.main:app --app-dir backend --port 8000

