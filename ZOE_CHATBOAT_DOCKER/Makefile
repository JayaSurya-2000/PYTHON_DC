default: build


build:
	docker-compose build --no-cache

build-dev:
	docker-compose -f docker-compose-dev.yml build --no-cache

run:
	docker-compose down
	docker-compose up -d

run-dev:
	docker-compose -f docker-compose-dev.yml down
	docker-compose -f docker-compose-dev.yml up -d

stop:
	docker-compose down

stop-dev:
	docker-compose -f docker-compose-dev.yml down
