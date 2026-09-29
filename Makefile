install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

api:
	uvicorn app.api.main:app --reload

ui:
	streamlit run frontend/streamlit_app.py

test:
	pytest -q

lint:
	ruff check .

format:
	ruff format .

ingest-sample:
	python scripts/ingest_sample.py

evaluate:
	python evaluation/evaluate_retrieval.py

docker-up:
	docker compose up --build
