#!/bin/bash

# List aurora dbs with maintance windows
aws rds describe-db-clusters --filters Name=engine,Values=aurora-postgresql --query "DBClusters[*].{Name:DBClusterIdentifier,Version:EngineVersion,Maintance:PreferredMaintenanceWindow}"
