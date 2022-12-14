start:
	python main.py

build:
	docker compose up --build -d --remove-orphans

up:
	docker compose up -d

down:
	docker compose down

down-v:
	docker compose down -v

db:
	docker compose exec db psql --username=delivery --dbname=pizza_delivery

init-db:
	python init_db.py

stop-db:
	docker stop db

check-db:
	docker exec -it db psql -U postgres
