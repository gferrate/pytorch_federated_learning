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

del_logs:
	tar -czvf logs_bak.tar.gz logs/*.log
	rm logs/*.log
