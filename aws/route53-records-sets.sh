#!/bin/bash

HOSTED_ZONE_ID=$1

aws route53 list-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID

aws route53 list-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID --query "ResourceRecordSets[?Name == 'datadog-agent-internal-eks.eu-west-1.dev.hbi.systems.'].ResourceRecords"

aws route53 list-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID --query "ResourceRecordSets[?Name == 'datadog-agent-internal-eks.eu-west-1.dev.hbi.systems.']"

aws route53 list-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID --query "ResourceRecordSets[?Name == 'datadog-agent-internal-eks.eu-west-1.dev.hbi.systems.'].ResourceRecords" --output text > output

aws route53 list-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID --query "ResourceRecordSets[?Name == 'datadog-agent-internal-eks.eu-west-1.dev.hbi.systems.'].ResourceRecords[*].Value" --output text > output