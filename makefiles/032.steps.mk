login:
	$(aws ecr get-login --region eu-west-1)
build:
	docker build -t <name> .
tag:
	docker tag <name>:<tag> <repo>:<tag>
push:
	docker push <repo>:<tag>
full: login build tag push
