all: build run
stop: rm rmi
build:
	docker build --no-cache -t mainfastapi .
run:
	docker run -it -d -p 3000:3000 --name mainfastapi --env-file .env mainfastapi
exec:
	docker exec -it mainfastapi /bin/bash
logs:
	docker logs mainfastapi
ps:
	docker ps -a
img:
	docker images
rm:
	docker rm -f $$(docker ps -aq)
rmi:
	docker rmi -f $$(docker images -q)