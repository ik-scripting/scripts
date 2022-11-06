#!/bin/bash

# ./create-role.sh --create
# ./create-role.sh --delete
# 57 characters
name="ik-test-9f3da91c-5df7-11ed-a319-935397d01831-575e5f629803"
path="/eu-west-1/ns/eks-cluster-sandbox/"

usage() {
  echo "Usage: for $0"
cat << EOF

Documentation https://docs.aws.amazon.com/cli/latest/reference/iam/index.html#cli-aws-iam

Usage: $(basename "$0") <options>
    -h, --help       Display help
    -c, --create     Create role
    -d, --delete     Delete role
EOF
}

create() {
  echo "Create IAM role"
  aws iam create-role \
    --role-name "$name" \
    --path "$path" \
    --assume-role-policy-document file://trust.json \
    --description "IAM role test path"
}

delete() {
  echo "Delete IAM role"
  aws iam delete-role \
    --role-name "$name"
}

cmds() {
  while :; do
    case "${1:-}" in
        -c|--create)
          create
          break
          ;;
        -d|--delete)
          delete
          break
          ;;
        -h|--help)
          usage
          break
          ;;
        *)
          usage
          break
          ;;
    esac
    shift
  done
}

cmds "$@"
