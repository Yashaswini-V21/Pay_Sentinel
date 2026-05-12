dev:
	cd backend/src && python app.py

prod:
	docker-compose -f docker-compose.prod.yml up -d

build:
	docker build --target production -t paysentinel:latest .

test:
	pytest tests/unit -v

test-integration:
	pytest tests/integration -v

kafka:
	docker-compose up -d

logs:
	docker-compose -f docker-compose.prod.yml logs -f paysentinel

clean:
	find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null; true

health:
	curl -s http://localhost/api/health | python -m json.tool

metrics:
	curl -s http://localhost/api/metrics | python -m json.tool
