#!/bin/bash
# https://www.dba-ninja.com/2022/09/aws-cli-cheatsheet.html

# List aurora dbs with maintance windows
aws rds describe-db-clusters --filters Name=engine,Values=aurora-postgresql --query "DBClusters[*].{Name:DBClusterIdentifier,Version:EngineVersion,Maintance:PreferredMaintenanceWindow}" --output=table
