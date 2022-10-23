# Drain Nodes

Why? We should not document commands [confluence](https://hbidigital.atlassian.net/wiki/spaces/PAAS/pages/5524815905/Kubernetes+EKS+Upgrade)
as doing it in dev/prod manually just a noncence and will lead to multiple errors, incidents and increasing number of postmortems.

## Getting started

```sh
pip install pipenv
cd cli-dain-nodes && pipenv shell
pipenv sync
./main.py --help
# cleanup venv
rm -rf $(pipenv --venv)
pipenv --rm
# show dependencies
pipenv graph
```

As well as kubectl clt context should be set example `[eks:448714108511]::eks-cluster-dev(ns:kube-system)`
and commoand should succeed `kubectl get nodes`

The AWS context should be set as well. The commands `aws s3 ls` should execute successfuly.

### Optional Dependencies

```sh
brew install python-tk
```

## Commands

The cli read configuration from [this](./config.yaml) file

## Taint nodes

Taint all nodes in ASG (legacy/new)

```sh
./main.py --taints
```

## Scale Down ASG

Taint all nodes in ASG (legacy/new)

```sh
./main.py --migrage_asg
```

## Recycle

Recycle all nodes with specific selector

```sh
./main.py --recycle
```

## Expect Worker nodes with following selectors

```sh
k get nodes --selector='group-name=ondemand-cluster-resources-group1-1.20'
k get nodes --selector='group-name=apm-enabled-spot-worker-group1-1.20'
k get nodes --selector='eks-self-managed=true'
k get nodes --selector='group-name=spot-worker-group1-1.20'
k get nodes --selector='node.kubernetes.io/lifecycle=ondemand,dedicated=cluster-resources'
k get nodes --selector='group-name=ondemand-airflow-group1-1.20'
k get nodes --selector='group-name=test-spot-worker-group2-1.20'
k get pods --selector='apm=enabled'
```

k get deploy | grep "0/"

## Todo

- [ ] Rewrite in GO and create binary
- [ ] Dry run
- [X] Read config from a file
- [X] Untaint ASG
- [ ] Send statistics to Datadog
- [X] Slack notification

## Resources

- [Terraform kubernetes provider](https://github.com/hashicorp/terraform-provider-kubernetes)
- [Python packaging](https://iq-inc.com/importerror-attempted-relative-import/)
- [Boto3: ASG](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/autoscaling.html)
- [Emojies](https://github.com/ikatyang/emoji-cheat-sheet/blob/master/README.md)
- [Docs](https://hbidigital.atlassian.net/wiki/spaces/PAAS/pages/5524815905/Kubernetes+EKS+Upgrade)
