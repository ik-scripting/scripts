# Drain Nodes

This cli covers how to configure a Kubernetes service account to assume an AWS Identity and Access Management (IAM) role. Any pods that are configured to use the service account can then access any AWS service that the role has permissions to access.

## Getting started

```sh
pip install pipenv
cd k8s/cli-pod-web-identity && pipenv shell
pipenv sync
./main.py --help
# cleanup venv
rm -rf $(pipenv --venv)
pipenv --rm
# show dependencies
pipenv graph
```

The AWS context should be set as well. The commands `aws s3 ls` should execute successfuly.

## Commands

## Create an IAM role

Taint all nodes in ASG (legacy/new)

```sh
./main.py --create
```

## Todo

- [ ] Dry run

## Resources

- [AWS Docs](https://docs.aws.amazon.com/eks/latest/userguide/associate-service-account-role.html)
- [Boto3 Exception Handling](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/error-handling.html)
- [Pod Identity WebHook](https://github.com/aws/amazon-eks-pod-identity-webhook)
