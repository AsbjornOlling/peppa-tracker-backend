run:
	uvicorn main:app --reload

docker-test: docker-run
	docker-compose exec app coverage run -m pytest tests.py
	docker-compose exec app coverage report
	docker-compose exec app coverage html
	# notice that this target does not stop the containers afterwards

docker-run:
	docker-compose up --build -d
