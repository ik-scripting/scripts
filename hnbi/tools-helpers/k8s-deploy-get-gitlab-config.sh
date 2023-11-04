#!/usr/bin/env bash

# get k8s aplication deployment config files via Gitlab API from projects that belong to the below subgroups
# requres a Gitlab API token

ENV=dev
WORKDIR=.
subgroups=(
  6263906   # example-workflows
  7689678   # shared-projects
)

for subgroup in "${subgroups[@]}"; do
  echo subgroup: $subgroup
  projects=()
  page=1
  while :; do
    echo page: $page
    output=$(curl -s --header "PRIVATE-TOKEN: $TOKEN" "https://gitlab.com/api/v4/groups/$subgroup/projects?include_subgroups=true&page=$page" | jq -r '.[].id')
    if [[ -z $output ]]; then
      break
    fi
    projects+=(${output[@]})
    page=$((page+1))
    sleep 1
  done

  for project in "${projects[@]}"; do
    output=$(curl -s --header "PRIVATE-TOKEN: $TOKEN" "https://gitlab.com/api/v4/projects/$project/repository/files/k8s%2F$ENV%2Fconfig%2Eyaml/raw?ref=master")
    name=$(echo "$output" | grep -E "^name:" | cut -d " " -f 2)
    if [[ -n $name ]]; then
      path="$WORKDIR/values/$subgroup-$name-$project-values.yaml"
      echo "config values found for $name!"
      echo "$output" > "$path"
    fi
  done
done
