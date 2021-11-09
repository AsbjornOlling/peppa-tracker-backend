run:
	uvicorn main:app --reload

test:
	docker-compose up --build -d
	docker-compose exec app pytest tests.py
	# notice that this target does not stop the containers afterwards
