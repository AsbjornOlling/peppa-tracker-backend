run:
	uvicorn main:app --reload

docker-test: docker-run
	docker-compose exec app pytest tests.py
	# notice that this target does not stop the containers afterwards

docker-run:
	docker-compose up --build -d
