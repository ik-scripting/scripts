VERSION=$(shell git rev-parse --short HEAD)
DESC=$(shell git log -1 --pretty=%B)
BUCKET_NAME="my-bucket"
PROJECT_NAME="my-project"
REGION="us-east-1"
ENV_NAME="elasticbeanstalk-environment-name"

archive:
	git archive --format=zip -o $(VERSION).zip HEAD

create_version:
	aws s3 cp $(VERSION).zip s3://$(BUCKET_NAME)/$(PROJECT_NAME)/
	aws elasticbeanstalk create-application-version --application-name $(PROJECT_NAME) --description "$(DESC)" --version-label $(VERSION) --source-bundle S3Bucket="$(BUCKET_NAME)",S3Key="$(PROJECT_NAME)/$(VERSION).zip" --region $(REGION)

update_environment:
	aws elasticbeanstalk update-environment --environment-name $(ENV_NAME) --version-label $(VERSION) --region $(REGION)

clean_deploy:
	rm $(VERSION).zip

deploy: archive create_version update_environment clean_deploy
