run:
	docker-compose up
build:
	docker-compose up --build
tests:
	docker exec -it exchange-rate-fastapi-1 pytest