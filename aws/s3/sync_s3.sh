# Copy log files to S3 with server-side encryption enabled.
# Then, if successful, delete log files that are older than a day.
LOG_DIR="/var/log/bastion/"
PREFIX="logs"
BUCKET="hermes-sharedservices-data"
REGION="eu-west-1"
aws s3 cp $LOG_DIR s3://$BUCKET/$PREFIX/ --sse --region $REGION --recursive && find $LOG_DIR* -mtime +1 -exec rm {} \;
