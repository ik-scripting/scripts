#!/bin/bash
# https://www.dba-ninja.com/2022/09/aws-cli-cheatsheet.html

# List aurora dbs with maintance windows, and teams
aws rds describe-db-clusters --filters Name=engine,Values=aurora-postgresql --query "DBClusters[*].{Team:TagList[?Key=='team'].Value | [0],Name:DBClusterIdentifier,Version:EngineVersion,Maintance:PreferredMaintenanceWindow}" --output=table

aws rds describe-db-instances --filters Name=engine,Values=postgres --query "DBInstances[*].{Team:TagList[?Key=='team'].Value | [0],Name:DBInstanceIdentifier,Version:EngineVersion,Maintance:PreferredMaintenanceWindow}" --output=table

# list snapshots
aws rds describe-db-snapshots --db-instance-identifier $DB_NAME \
--query "DBSnapshots[*].{Name:DBSnapshotIdentifier,CreationTime:SnapshotCreateTime,Arn:DBSnapshotArn}" --output=table

# Only specific version
aws rds describe-db-instances \
  --query "DBInstances[?Engine=='postgres' && EngineVersion<'15'].DBInstanceIdentifier" \
  --output json | jq .

aws rds describe-db-instances --filters Name=engine,Values=mysql \
  --query "DBInstances[?EngineVersion<'9'].{Team:TagList[?Key=='team'].Value | [0],Name:DBInstanceIdentifier,Version:EngineVersion,Maintance:PreferredMaintenanceWindow}" \
  --output=table

# db migration https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.PostgreSQL.html#USER_UpgradeDBInstance.PostgreSQL.MajorVersion
aws rds describe-db-engine-versions --engine postgres  --engine-version your-version --query "DBEngineVersions[*].ValidUpgradeTarget[*].{EngineVersion:EngineVersion}" --output text

Sean Green SeanGreen@hollandandbarrett.com
Paris Apostolopoulos ParisApostolopoulos@hollandandbarrett.com
Jonathan Payne JonPayne1@hollandandbarrett.com
Timur Igorevich TimurIgorevich@hollandandbarrett.com
Sara Stirk-Williams SaraStirk-Williams@hollandandbarrett.com

Sergey Svistunov SergeySvistunov@hollandandbarrett.com