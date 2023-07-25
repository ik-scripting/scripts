DOCKER_REPO := repo
NAMESPACE := everyone
CONTAINER := terraform

docker-build: ## Build the container
    docker build -t $(NAMESPACE)/$(CONTAINER):latest .

# HELP
# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html

help: ## This help.
    @awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

globals: ## Auto login to ECR
    @echo 'Auto login to AWS ECR using aws clid'
    @eval $$(aws ecr get-login --no-include-email)

publish-latest: docker-build ## Publish the `latest` taged container to ECR
    docker tag $(NAMESPACE)/$(CONTAINER):latest $(DOCKER_REPO)/$(NAMESPACE)/$(CONTAINER):latest
    @echo 'publish latest to $(DOCKER_REPO)'
    docker push $(DOCKER_REPO)/$(NAMESPACE)/$(CONTAINER):latest

# disallow any parallelism (-j) for Make. This is necessary since some
# commands during the build process create temporary files that collide
# under parallel conditions.
.NOTPARALLEL:

all: globals docker-build publish-latest
