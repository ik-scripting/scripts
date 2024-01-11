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

aws rds describe-db-instances --filters Name=engine,Values=postgres \
  --query "DBInstances[?EngineVersion<'15'].{Team:TagList[?Key=='team'].Value | [0],Name:DBInstanceIdentifier,Version:EngineVersion,Maintance:PreferredMaintenanceWindow}" \
  --output=table
