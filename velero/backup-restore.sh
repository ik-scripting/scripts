#!/bin/bash

# Purpose - Backup & Restore workloads
# Prerequisits
# brew install velero
# Usage
# ./bin/backup-restore.sh -b true -n cicd
# ./bin/backup-restore.sh -r true -n cicd

set -eu

: "${ENV}"
: "${KUBECONFIG}"

function help_text {
    cat <<EOF
    Usage: $0 [ -b|--backup BACKUP ] [ -r|--restore RESTORE ] [ -n|--namespace NAMESPACE ] [-h]
        BACKUP     (optional) Work with backups.
        RESTORE    (optional) Work with restores.
        NAMEESPACE (optional) Namespaces to include in the backup
EOF
    exit 1
}

BACKUP=""
RESTORE=""
NAMESPACE=""
DATE=$(date +%F)

while [ $# -gt 0 ]; do
    arg=$1
    case $arg in
        -h|--help)
            help_text
        ;;
        -b|--backup)
            BACKUP="$2"
            shift; shift
        ;;
        -r|--restore)
            RESTORE="$2"
            shift; shift
        ;;
        -n|--namespace)
            NAMESPACE="$2"
            shift; shift
        ;;
        *)
            echo "ERROR: Unrecognised option: ${arg}"
            help_text
            exit 1
        ;;
    esac
done

if [ -n "${BACKUP}" ] && [ -n "${RESTORE}" ];
then
  echo "cannot set BACKUP and RESTORE at the same time"
  exit 1
fi

if [ -n "${RESTORE}" ];then
  echo "./bin/backup-restore.sh -r -n=${NAMESPACE}"
  echo "run: velero backup get"
  echo "run: velero restore create --from-backup <NAME> --include-namespaces ${NAMESPACE}"
fi

###############################################
# Perform full backup
# $BACKUP set to a boolean (1)
# $NAMESPACE unset (2)
################################################
if [ "${BACKUP}" == "true" ] && [ -z "${NAMESPACE}" ];
then
    # backup_full
  echo "backup in full"
  velero backup create backup-full --snapshot-volumes=false --kubeconfig "${KUBECONFIG}" --wait
fi

###############################################
# Perform backup for namespace
# $BACKUP set to a boolean (1)
# $NAMESPACE is set to string (2)
################################################
if [ "${BACKUP}" == "true" ] && [ -n "${NAMESPACE}" ]
then
  echo "backup in namespace ${NAMESPACE}"
  velero backup create "backup-${NAMESPACE}-${DATE}" --snapshot-volumes=true --include-namespaces "${NAMESPACE}" --kubeconfig "${KUBECONFIG}"
  echo "run 'velero backup describe backup-cicd'"
fi

# k get configmap aws-auth -o yaml > aws-auth.dev.yaml
# k get configmap aws-auth -o yaml > aws-auth.stage.yaml
# k get configmap aws-auth -o yaml > aws-auth.prod.yaml
