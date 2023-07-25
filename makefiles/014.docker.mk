install: composer database cc

database:
    docker run --rm -it -v $(pwd):/app $IMAGE_NAME \
        /bin/bash -ci "app/console doctrine:database:create"
    docker run --rm -it -v $(pwd):/app $IMAGE_NAME \
        /bin/bash -ci "app/console doctrine:schema:create"
    docker run --rm -it -v $(pwd):/app $IMAGE_NAME \
        /bin/bash -ci "app/console doctrine:schema:update"
    
composer:
    docker run --rm -it -v $(pwd):/app $IMAGE_NAME \
        /bin/bash -ci "composer install --prefer-dist"

cc:
    docker run --rm -it -v $(pwd):/app $IMAGE_NAME \
        /bin/bash -ci "app/console cache:clear --env=prod"
