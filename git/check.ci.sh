#!/bin/bash
# vim: set ft=sh

set -e

exec 3>&1 # make stdout available as fd 3 for the result
exec 1>&2 # redirect all output to stderr for logging

source $(dirname $0)/common.sh

# for jq
PATH=/usr/local/bin:$PATH

payload=$TMPDIR/git-resource-request

cat > $payload <&0

load_pubkey $payload
configure_https_tunnel $payload
configure_git_ssl_verification $payload
configure_credentials $payload

uri=$(jq -r '.source.uri // ""' < $payload)
branch=$(jq -r '.source.branch // ""' < $payload)
paths="$(jq -r '(.source.paths // ["."])[]' < $payload)" # those "'s are important
ignore_paths="$(jq -r '":!" + (.source.ignore_paths // [])[]' < $payload)" # these ones too
tag_filter=$(jq -r '.source.tag_filter // ""' < $payload)
git_config_payload=$(jq -r '.source.git_config // []' < $payload)
ref=$(jq -r '.version.ref // ""' < $payload)
skip_ci_disabled=$(jq -r '.source.disable_ci_skip // false' < $payload)
filter_whitelist=$(jq -r '.source.commit_filter.include // []' < $payload)
filter_blacklist=$(jq -r '.source.commit_filter.exclude // []' < $payload)
reverse=false

configure_git_global "${git_config_payload}"

destination=$TMPDIR/git-resource-repo-cache

tagflag=""
if [ -n "$tag_filter" ]; then
  tagflag="--tags"
fi

# We're just checking for commits; we don't ever need to fetch LFS files here!
export GIT_LFS_SKIP_SMUDGE=1

if [ -d $destination ]; then
  cd $destination
  git fetch $tagflag -f
  git reset --hard FETCH_HEAD
else
  branchflag=""
  if [ -n "$branch" ]; then
    branchflag="--branch $branch"
  fi

  git clone --single-branch $uri $branchflag $destination $tagflag
  cd $destination
fi

if [ -n "$ref" ] && git cat-file -e "$ref"; then
  init_commit=$(git rev-list --max-parents=0 HEAD)
  if [ "${ref}" = "${init_commit}" ]; then
    reverse=true
    log_range="HEAD"
  else
    reverse=true
    log_range="${ref}~1..HEAD"
  fi
else
  log_range=""
  ref=""
fi

if [ "$paths" = "." ] && [ -z "$ignore_paths" ]; then
  paths_search=""
else
  paths_search=`echo "-- $paths $ignore_paths" | tr "\n\r" " "`
fi

list_command="git rev-list --all --first-parent $log_range $paths_search"
if [ `echo $filter_whitelist | jq -r '. | length'` -gt 0 ]
then
    whitelist_items=$(echo $filter_whitelist | jq -r -c '.[]')
    for wli in "$whitelist_items"
    do
        list_command+=" | git rev-list --stdin --grep=\"$wli\" --first-parent --no-walk"
    done
fi

if [ `echo $filter_blacklist | jq -r '. | length'` -gt 0 ]
then
    blacklist_items=$(echo $filter_blacklist | jq -r -c '.[]')
    for bli in "$blacklist_items"
    do
        list_command+=" | git rev-list --stdin --grep=\"$bli\" --invert-grep --first-parent --no-walk"
    done
fi


if [ "$skip_ci_disabled" != "true" ]; then
  list_command+=" | git rev-list --stdin --grep=\"\\[ci\\sskip\\]\" --grep=\"\\[skip\\sci\\]\" --invert-grep --first-parent --no-walk"
fi

replace_escape_chars() {
  sed -e 's/[]\/$*.^[]/\\&/g' <<< $1
}

lines_including_and_after() {
  local escaped_string=$(replace_escape_chars $1)
  sed -ne "/$escaped_string/,$ p"
}

get_commit(){
  for tag in $*; do
    commit=$(git rev-list -n 1 $tag)
    jq -n '{ref: $tag, commit: $commit}' --arg tag $tag --arg commit $commit
  done
}

#if no range is selected just grab the last commit that fits the filter
if [ -z "$log_range" ]
then
    list_command+="| git rev-list --stdin -1"
fi

if [ "$reverse" == "true" ]
then
    list_command+="| git rev-list --stdin --first-parent --no-walk --reverse"
fi

if [ -n "$tag_filter" ]; then
  {
    if [ -n "$ref" ] && [ -n "$branch" ]; then
      tags=$(git tag --list "$tag_filter" --sort=creatordate --contains $ref --merged $branch)
      get_commit $tags
    elif [ -n "$ref" ]; then
      tags=$(git tag --list "$tag_filter" --sort=creatordate | lines_including_and_after $ref)
      get_commit $tags
    else
      branch_flag=
      if [ -n "$branch" ]; then
        branch_flag="--merged $branch"
      fi
      tag=$(git tag --list "$tag_filter" --sort=creatordate $branch_flag | tail -1)
      get_commit $tag
    fi
  } | jq -s "map(.)" >&3
else
  {
    set -f
    eval "$list_command"
    set +f
  } | jq -R '.' | jq -s "map({ref: .})" >&3
fi
