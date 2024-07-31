all: build run
stop: rm rmi
build:
	docker-compose up --build
run:
	docker run -it -d -p 3500:3500 --name external --env-file .env external
exec:
	docker exec -it external /bin/bash
logs:
	docker logs external
ps:
	docker ps -a
img:
	docker images
rm:
	docker rm -f $$(docker ps -aq)
rmi:
	docker rmi -f $$(docker images -q)
tag:
	docker tag external wjdguswn1203/external:latest
push:
	docker push wjdguswn1203/external:latest
pull:
	docker pull wjdguswn1203/external:latest