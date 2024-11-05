#!/bin/sh

# How to Gitlab CI LINT

# in 'paas-go/.gitlab/common.gitlab-ci.yml#lint'

echo "# run gofmt to validate formats for Go program. 'gofmt -d -l .'"
# required, as gofmt excit code is always zero
if [ -z "$(gofmt -l .)" ]; then
    echo -e "${TXT_BLUE}All files are properly formatted.${TXT_CLEAR}"
else
    echo -e "${TXT_YELLOW}Please run 'make lint' to fix. Some files need formatting:${TXT_CLEAR}"
    gofmt -d -l .
    exit 1
fi

echo "# run go mod tidy to validate dependencies. 'go mod tidy -v'"
cp go.mod go-mod
go mod tidy -v > /dev/null 2>result
cat result

if grep -q "unused" result; then
    echo -e "${TXT_YELLOW}Error: Unused dependencies detected. Please run 'go mod tidy' and commit the changes.${TXT_CLEAR}"
    git diff --exit-code -- go-mod go.mod
    exit 1
fi

echo "golangci-lint run --timeout ${LINT_TIMEOUT:-5}m"
golangci-lint --version
golangci-lint run --timeout "${LINT_TIMEOUT:-5}m"
