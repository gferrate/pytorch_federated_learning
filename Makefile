build:
	docker build -t pytorch_fl .

run:
	docker-compose up -d

stop:
	docker-compose down

update:
	docker-compose down
	docker build -t pytorch_fl .
	docker-compose up -d
prepare:
	touch logs/client_8003.log
	touch logs/client_8004.log
	touch logs/main_server.log
	touch logs/secure_aggregator.log
