#!/bin/bash

HOSTED_ZONE_ID=Z1HLSICRCJVNZR

aws route53 list-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID

# how to use contains in query
aws route53 list-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID --query "ResourceRecordSets[?contains(Name, 'plm-category') == \`true\`]"

aws route53 list-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID --query "ResourceRecordSets[?Name == 'datadog-agent-internal-eks.eu-west-1.dev.hbi.systems.'].ResourceRecords"

aws route53 list-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID --query "ResourceRecordSets[?Name == 'datadog-agent-internal-eks.eu-west-1.dev.hbi.systems.']"

aws route53 list-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID --query "ResourceRecordSets[?Name == 'datadog-agent-internal-eks.eu-west-1.dev.hbi.systems.'].ResourceRecords" --output text > output

aws route53 list-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID --query "ResourceRecordSets[?Name == 'datadog-agent-internal-eks.eu-west-1.dev.hbi.systems.'].ResourceRecords[*].Value" --output text > output


aws route53 list-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID --query "ResourceRecordSets[?Name == 'plm-category-service-\\045\\041s\\050\\074nil\\076\\051-internal-eks.eu-west-1.dev.hbi.systems.']"

aws route53 change-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID --change-batch file:///delete.json
