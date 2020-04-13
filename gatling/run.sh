#!/bin/bash
function help_text {
    cat <<EOF
    Usage: $0 [ -p|--profile PROFILE ] [ -r|--report-bucket REPORT_BUCKET ] [-h]
        PROFILE         (optional) The profile to use from ~/.aws/credentials.
        REPORT_BUCKET   (required) name of the S3 bucket to upload the reports to. Must be in same AWS account as profile.
                                   It must be provided.
EOF
    exit 1
}

# Running performance test
mvn gatling:test -o

#Upload reports
for _dir in target/gatling/*/
do
  dir="$(basename ${_dir})"
  cp -R ${_dir}/. /reports/
done

# do
#    aws s3 cp ${_dir}simulation.log s3://${REPORT_BUCKET}/logs/$HOSTNAME-simulation.log
# done
