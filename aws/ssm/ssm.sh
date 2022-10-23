#!/bin/bash

# https://docs.aws.amazon.com/systems-manager/latest/userguide/param-create-cli.html

aws ssm put-parameter --name "/test-secrets-csi-driver/test" --value "my-secret-value-123" --type SecureString --tags "Key=who,Value=ik"
aws ssm get-parameter --name "/test-secrets-csi-driver/test" --query "Parameter.Value" --with-decryption
aws ssm delete-parameter --name "test-secrets-csi-driver/test"