#!/usr/bin/env bash

function check_bash() {
find . -name "*.sh" | while IFS= read -d '' -r file;
do
  if [[ "$file" != *"bash -e"* ]];
  then
    echo "$file is missing shebang with -e";
    exit 1;
  fi;
done;
}

# This function makes sure that the required files for
# releasing to OSS are present
function basefiles() {
  echo "Checking for required files"
  test -f CONTRIBUTING.md || echo "Missing CONTRIBUTING.md"
  test -f LICENSE || echo "Missing LICENSE"
  test -f README.md || echo "Missing README.md"
}

# This function runs the hadolint linter on
# every file named 'Dockerfile'
function docker() {
  echo "Running hadolint on Dockerfiles"
  find . -name "Dockerfile" -exec hadolint {} \;
}

# This function runs 'terraform validate' against all
# files ending in '.tf'
function check_terraform() {
  echo "Running terraform validate"
  #shellcheck disable=SC2156
  find . -name "*.tf" -exec bash -c 'terraform validate $(dirname "{}")' \;
}

# This function runs 'go fmt' and 'go vet' on eery file
# that ends in '.go'
function golang() {
  echo "Running go fmt and go vet"
  find . -name "*.go" -exec go fmt {} \;
  find . -name "*.go" -exec go vet {} \;
}

# This function runs the flake8 linter on every file
# ending in '.py'
function check_python() {
  echo "Running flake8"
  find . -name "*.py" -exec flake8 {} \;
}

# This function runs the shellcheck linter on every
# file ending in '.sh'
function check_shell() {
  echo "Running shellcheck"
  find . -name "*.sh" -exec shellcheck -x {} \;
}

# This function makes sure that there is no trailing whitespace
# in any files in the project.
# There are some exclusions
function check_trailing_whitespace() {
  echo "The following lines have trailing whitespace"
  grep -r '[[:blank:]]$' --exclude-dir=".terraform" --exclude="*.png" --exclude-dir=".git" --exclude="*.pyc" .
  rc=$?
  if [ $rc = 0 ]; then
    exit 1
  fi
}
