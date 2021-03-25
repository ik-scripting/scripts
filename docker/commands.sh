#!/bin/sh

echo "Remove all images"

docker system prune
docker container prune
docker images prune
docker system prune -a
# delete all docker containers
docker rm $(docker ps -a -q)
# remove all docker images
docker rmi $(docker images -q)
docker system prune --volumes --force
# stop all docker containers
docker stop $(docker ps -q) || true
docker system prune -a -f
docker volume rm $(docker volume ls -q) || true
# tail output of application on container
docker logs -f &lt;container_id&gt;
docker logs nginx --follow

echo "Could not connect to a Docker daemon"
sudo usermod -aG docker $USER
sudo usermod -a -G docker ec2-user

echo "Remove all untagged images"
container prune -f
docker rmi $(docker images -a | grep "^<none>" | awk '{print $3}') -f
docker image prune --force --filter "repository=none"
docker container rm $(docker container ls -aq)

echo "Run image"
docker build -t node-distroless .
docker run -p 3000:3000 -ti --rm --init node-distroless
# This will run the previously built image on the docker machine and map port 8080 on the docker-machine to port 80 on the container
docker run -d -p 8080:80 nginx

echo "Docker Compose"
# this will start all services using compose on the docker machine -d is important, as this will detach
docker-compose up -d
# this will rm all containers associated with the services using compose
docker-compose rm
# this will stop all services using compose
docker-compose stop