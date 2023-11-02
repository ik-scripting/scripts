#!/usr/bin/env python3

# pylint: disable=invalid-name

""" Wiz : Resource Count : AWS """

import argparse
import concurrent.futures
import signal
import sys

# As a single script download, we do not publish a requirements.txt. Autodocument.

try:
    import boto3
    from botocore.config import Config
except ImportError:
    print("\nERROR: Missing required AWS SDK packages. Run the following command to install/upgrade:\n")
    print("pip3 install --upgrade boto3 botocore")
    sys.exit(1)


version='2.1.0'


####
# Command Line Arguments
####


parser = argparse.ArgumentParser(description = 'Get AWS Resource Counts')
parser.add_argument(
    '--all',
    action = 'store_true',
    dest = 'all',
    help = 'Get resources from the AWS Organization (default: false)',
    default = False
)
parser.add_argument(
    '--data',
    action = 'store_true',
    dest = 'data_mode',
    help = 'Get resources for DSPM (default: false)',
    default = False
)
parser.add_argument(
    '--debug',
    action = 'store_true',
    dest = 'debug_mode',
    help = 'Output debugging information (default: false)',
    default = False
)
parser.add_argument(
    '--gov',
    action = 'store_true',
    dest = 'use_gov',
    help = 'Use GovCloud regions (default: false)',
    default = False
)
parser.add_argument(
    '--safe',
    action = 'store_true',
    dest = 'safe_mode',
    help = 'Disable parallel processing (default: false)',
    default = False
)
args = parser.parse_args()


####
# Configuration and Globals
####


output_file = 'aws-resources.csv'
resource_count_column_width = 6
totals = []

try:
    aws_api_config = Config(
        retries = {
            'max_attempts' : 10,
            'mode'         : 'adaptive'
        }
    )
except Exception as ex0:  # pylint: disable=broad-exception-caught
    print("\nERROR: ")
    print(ex0)
    print("Unable to authenticate. Please verify your configuration")
    sys.exit(0)


####
# Common Library Code
####


def signal_handler(_signal_received, _frame):
    """ Control-C """
    print("\nExiting")
    sys.exit(0)


def resource_print(resource_count, resource_type, region='', account='', details=''):
    """ Resource output """
    rc = str(resource_count).rjust(resource_count_column_width)
    # Split and join to remove multiple spaces when variables are empty.
    print(' '.join(f"- {rc} {resource_type} in {region} {account} {details}".split()))


def debug_print(debug_data):
    """ Debug output """
    if args.debug_mode:
        print(f"\nDEBUG: {debug_data}")


def error_print(error_data):
    """ Error output """
    print(f"\nERROR: {error_data}")


####
# Customized Library Code
####


# Pagination:
# Some AWS services use NextToken, nextToken, Marker, or Marker/NextMarker:
# https://github.com/iann0036/aws-pagination-rules/blob/master/README.md
# See also: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/paginators.html


def select_east_region():
    """ Select the default region based upon environment """
    if args.use_gov:
        return 'us-gov-east-1'
    return 'us-east-1'


# Subscriptions (aka AWS Accounts)


def get_aws_organization():
    """ Get Active Accounts in an AWS Organization """
    root_account_id = None
    accounts = []
    try:
        client = boto3.client('organizations', config=aws_api_config)
        root_account_id = client.describe_organization()['Organization']['MasterAccountId']
        response = client.list_accounts()
    except Exception as ex:  # pylint: disable=broad-exception-caught
        error_print(ex)
        return root_account_id, accounts
    for account in response['Accounts']:
        debug_print(f"account: {account}")
        if account['Status'] != 'ACTIVE':
            continue
        accounts.append(account)
    while 'NextToken' in response:
        response = client.list_accounts(NextToken=response['NextToken'])
        for account in response['Accounts']:
            debug_print(f"account: {account}")
            if account['Status'] != 'ACTIVE':
                continue
            accounts.append(account)
    return root_account_id, accounts


def get_aws_account():
    """ Get AWS Account """
    account_id = None
    try:
        client = boto3.client('sts')
        account_id = client.get_caller_identity().get('Account')
    except Exception as ex:  # pylint: disable=broad-exception-caught
        error_print(ex)
    debug_print(f"account: {account_id}")
    return account_id, [{'Id': account_id, 'Name': account_id}]


def aws_assume_role(account_id, role_name, root_account_id):
    """ Assume role in target account """
    if account_id == root_account_id:
        try:
            session = boto3.Session()
            credentials = session.get_credentials()
            credentials = credentials.get_frozen_credentials()
            return {
                'AccessKeyId':     credentials.access_key,
                'SecretAccessKey': credentials.secret_key,
                'SessionToken':    credentials.token
            }
        except Exception as ex:  # pylint: disable=broad-exception-caught
            error_print(ex)
            return None
    try:
        client = boto3.client('sts', config=aws_api_config)
        assumed_role_object = client.assume_role(
            RoleArn='arn:aws:iam::' + str(account_id) + ':role/' + role_name,
            RoleSessionName='Session1'
        )
        credentials = assumed_role_object['Credentials']
        return {
            'AccessKeyId':     credentials['AccessKeyId'],
            'SecretAccessKey': credentials['SecretAccessKey'],
            'SessionToken':    credentials['SessionToken']
        }
    except Exception as ex:  # pylint: disable=broad-exception-caught
        error_print(ex)
        return None


def get_aws_regions():
    """ Get AWS Regions, using a us-east-1 region """
    regions = []
    try:
        session = boto3.session.Session()
        client = session.client('ec2', region_name=select_east_region())
        response = client.describe_regions()
    except Exception as ex:  # pylint: disable=broad-exception-caught
        error_print(ex)
        return regions
    regions = response['Regions']
    regions = sorted(regions, key=lambda d: d['RegionName'])
    debug_print(f"regions: {regions}")
    return regions


def get_aws_client(service, region, credentials):
    """ Return an AWS Client """
    try:
        client = boto3.client(
            service,
            region_name           = region,
            config                = aws_api_config,
            aws_access_key_id     = credentials['AccessKeyId'],
            aws_secret_access_key = credentials['SecretAccessKey'],
            aws_session_token     = credentials['SessionToken']
        )
    except Exception as ex:  # pylint: disable=broad-exception-caught
        error_print(ex)
        sys.exit(0)
    return client


# Virtual Machines: EC2 Instances


def get_aws_ec2_instances(region, credentials, account):
    """ Get AWS EC2 Instances (and the number of non-os disks) in the specified Account """
    instances_count = 0
    non_os_disks_count = 0
    client = get_aws_client('ec2', region, credentials)
    response = client.describe_instances(MaxResults=1000)
    for reservation in response['Reservations']:
        if 'Instances' in reservation:
            for instance in reservation['Instances']:
                debug_print(f"instance: {instance}")
                if instance['State']['Name'] == 'terminated':
                    continue
                instances_count += 1
                volumes_count, _ = get_aws_ebs_data_volume_info(region, credentials, instance)
                non_os_disks_count += volumes_count
    while 'NextToken' in response:
        response = client.describe_instances(NextToken=response['NextToken'], MaxResults=1000)
        for reservation in response['Reservations']:
            if 'Instances' in reservation:
                for instance in reservation['Instances']:
                    debug_print(f"instance: {instance}")
                    if instance['State']['Name'] == 'terminated':
                        continue
                    instances_count += 1
                    volumes_count, _ = get_aws_ebs_data_volume_info(region, credentials, instance)
                    non_os_disks_count += volumes_count

    if instances_count > 0 or args.debug_mode:
        resource_print(resource_count=instances_count, resource_type='virtual machines', region=region, account=account['Name'], details=f"with {non_os_disks_count} non os volumes")
        totals.append(['Virtual Machines', instances_count, account['Name'], account['Id'], region])
        totals.append(['Non-OS Disks', non_os_disks_count, account['Name'], account['Id'], region])


def get_aws_ebs_data_volume_info(region, credentials, instance):  # pylint: disable=unused-argument
    """ Get the volume count and size for data volumes of the specified Instance """
    volumes_count = 0
    volumes_size_gb = 0
    #client = get_aws_client('ec2', region, credentials)
    if len(instance['BlockDeviceMappings']) > 0:
        root_volume = instance['BlockDeviceMappings'][0]['Ebs']['VolumeId']
        for volume in instance['BlockDeviceMappings']:
            if volume['Ebs']['VolumeId'] != root_volume:
                volumes_count += 1
                #response = client.describe_volumes(VolumeIds=[volume['Ebs']['VolumeId']])
                #if len(response['Volumes']) > 0:
                #    volumes_size_gb += volumes[0]['Size']
    return volumes_count, volumes_size_gb


# Container Hosts: ECS


def get_aws_ecs_container_instances(region, credentials, account):
    """ Get AWS ECS Container Hosts in the specified Account """
    ecs_clusters = []
    ecs_instances_count = 0
    client = get_aws_client('ecs', region, credentials)
    response = client.list_clusters()
    ecs_clusters.extend(response['clusterArns'])
    while 'nextToken' in response:
        response = client.list_clusters(nextToken=response['nextToken'])
        ecs_clusters.extend(response['clusterArns'])
    for cluster in ecs_clusters:
        response = client.list_container_instances(cluster=cluster)
        ecs_instances_count += len(response['containerInstanceArns'])
        while 'nextToken' in response:
            response = client.list_container_instances(cluster=cluster, nextToken=response['nextToken'])
            ecs_instances_count += len(response['containerInstanceArns'])

    if ecs_instances_count > 0 or args.debug_mode:
        resource_print(resource_count=ecs_instances_count, resource_type='container instances', region=region, account=account['Name'])
        totals.append(['ECS Container Hosts', ecs_instances_count, account['Name'], account['Id'], region])


# Container Hosts: EKS


def get_aws_eks_instances(region, credentials, account):
    """ Get AWS EKS Container Hosts in the specified Account """
    eks_clusters = []
    eks_instances_count = 0
    eks_client = get_aws_client('eks', region, credentials)
    response = eks_client.list_clusters()
    eks_clusters.extend(response['clusters'])
    while 'nextToken' in response:
        response = eks_client.list_clusters(nextToken=response['nextToken'])
        eks_clusters.extend(response['clusters'])
    ec2_client = get_aws_client('ec2', region, credentials)
    # Search for instances with the 'kubernetes.io/cluster/<cluster-name>' tag per cluster
    for cluster in eks_clusters:
        response = ec2_client.describe_instances(Filters=[{'Name': 'tag-key', 'Values': ['kubernetes.io/cluster/' + cluster]}])
        for reservation in response['Reservations']:
            if 'Instances' in reservation:
                for instance in reservation['Instances']:
                    debug_print(f"instance: {instance}")
                    if instance['State']['Name'] == 'terminated':
                        continue
                    eks_instances_count += 1
        while 'NextToken' in response:
            response = ec2_client.describe_instances(Filters=[{'Name': 'tag-key', 'Values': ['kubernetes.io/cluster/' + cluster]}], NextToken=response['NextToken'])
            for reservation in response['Reservations']:
                if 'Instances' in reservation:
                    for instance in reservation['Instances']:
                        debug_print(f"instance: {instance}")
                        if instance['State']['Name'] == 'terminated':
                            continue
                        eks_instances_count += 1

    if eks_instances_count > 0 or args.debug_mode:
        resource_print(resource_count=eks_instances_count, resource_type='container host instances', region=region, account=account['Name'])
        totals.append(['EKS Container Hosts', eks_instances_count, account['Name'], account['Id'], region])


# Serverless Functions: Lambda Functions


def get_aws_lambda_functions(region, credentials, account):
    """ Get AWS Lambda Functions in the specified Account """
    serverless_functions_count = 0
    client = get_aws_client('lambda', region, credentials)
    response = client.list_functions(MaxItems=1000)
    serverless_functions_count += len(response['Functions'])
    while 'NextMarker' in response:
        response = client.list_functions(Marker=response['NextMarker'], MaxItems=1000)
        serverless_functions_count += len(response['Functions'])

    if serverless_functions_count > 0 or args.debug_mode:
        resource_print(resource_count=serverless_functions_count, resource_type='serverless functions', region=region, account=account['Name'])
        totals.append(['Serverless Functions', serverless_functions_count, account['Name'], account['Id'], region])


# Serverless Containers: ECS on Fargate


def get_aws_ecs_resources(region, credentials, account):
    """ Get AWS Fargate Containers in the specified Account """
    ecs_clusters = []
    ecs_containers_count = 0
    client = get_aws_client('ecs', region, credentials)
    response = client.list_clusters()
    ecs_clusters.extend(response['clusterArns'])
    while 'nextToken' in response:
        response = client.list_clusters(nextToken=response['nextToken'])
        ecs_clusters.extend(response['clusterArns'])
    for cluster in ecs_clusters:
        response = client.list_tasks(cluster=cluster, launchType='FARGATE')
        if response['taskArns']:
            describe_tasks_response = client.describe_tasks(cluster=cluster, tasks=response['taskArns'])
            for task in describe_tasks_response['tasks']:
                ecs_containers_count += len(task['containers'])
        while 'nextToken' in response:
            response = client.list_tasks(cluster=cluster, launchType='FARGATE', nextToken=response['nextToken'])
            if response['taskArns']:
                describe_tasks_response = client.describe_tasks(cluster=cluster, tasks=response['taskArns'])
                for task in describe_tasks_response['tasks']:
                    ecs_containers_count += len(task['containers'])

    if ecs_containers_count > 0 or args.debug_mode:
        resource_print(resource_count=ecs_containers_count, resource_type='serverless container tasks', region=region, account=account['Name'])
        totals.append(['Serverless Containers', ecs_containers_count, account['Name'], account['Id'], region])


# Container Registry Images: ECR


def get_aws_ecr_images(region, credentials, account):
    """ Get AWS ECR Images in the specified Account """
    ecr_repositories = []
    container_registry_images_count = 0
    client = get_aws_client('ecr', region, credentials)
    response = client.describe_repositories()
    ecr_repositories.extend(response['repositories'])
    while 'nextToken' in response:
        response = client.describe_repositories(nextToken=response['nextToken'])
        ecr_repositories.extend(response['repositories'])
    for repository in ecr_repositories:
        response = client.list_images(repositoryName=repository['repositoryName'])
        container_registry_images_count += len(response['imageIds'])
        while 'nextToken' in response:
            response = client.list_images(repositoryName=repository['repositoryName'], nextToken=response['nextToken'])
            container_registry_images_count += len(response['imageIds'])

    if container_registry_images_count > 0 or args.debug_mode:
        resource_print(resource_count=container_registry_images_count, resource_type='container registry images', region=region, account=account['Name'])
        totals.append(['Container Registry Images', container_registry_images_count, account['Name'], account['Id'], region])


# Data Buckets: S3 Buckets


def get_aws_s3_buckets(region, credentials, account):
    """ Get AWS S3 Buckets in the specified Account """
    buckets_count = 0
    client = get_aws_client('s3', region, credentials)
    response = client.list_buckets()
    buckets_count += len(response['Buckets'])
    while 'NextToken' in response:
        response = client.list_buckets(NextToken=response['NextToken'])
        buckets_count += len(response['Buckets'])

    if buckets_count > 0 or args.debug_mode:
        resource_print(resource_count=buckets_count, resource_type='buckets', region=region, account=account['Name'])
        totals.append(['Data Buckets', buckets_count, account['Name'], account['Id'], region])


# Data in Cloud-managed Databases (PaaS): RedShift


def get_aws_rds_instances(region, credentials, account):
    """ Get AWS RDS Instances in the specified Account """
    database_instances_count = 0
    client = get_aws_client('rds', region, credentials)
    response = client.describe_db_instances()
    database_instances_count += len(response['DBInstances'])
    while 'Marker' in response:
        response = client.describe_db_instances(Marker=response['Marker'])
        database_instances_count += len(response['DBInstances'])

    if database_instances_count > 0 or args.debug_mode:
        resource_print(resource_count=database_instances_count, resource_type='databases', region=region, account=account['Name'])
        totals.append(['Cloud-Managed Databases', database_instances_count, account['Name'], account['Id'], region])


# Data in Data Warehouses: DynamoDB


def get_aws_dynamodb_instances(region, credentials, account):
    """ Get AWS DynamoDB Tables in the specified Account """
    data_warehouses_count = 0
    client = get_aws_client('dynamodb', region, credentials)
    response = client.list_tables()
    data_warehouses_count += len(response['TableNames'])
    while 'LastEvaluatedTableName' in response:
        response = client.list_tables(ExclusiveStartTableName=response['LastEvaluatedTableName'])
        data_warehouses_count += len(response['TableNames'])

    if data_warehouses_count > 0 or args.debug_mode:
        resource_print(resource_count=data_warehouses_count, resource_type='data warehouses', region=region, account=account['Name'])
        totals.append(['Data Warehouses', data_warehouses_count, account['Name'], account['Id'], region])


####
# Main
####


def get_aws_resources(regions, account, root_account_id):
    """ Get billable resources """
    exceptions = 0
    credentials = aws_assume_role(account['Id'], 'OrganizationAccountAccessRole', root_account_id)
    if not credentials:
        error_print(f"Could not assume AWS Role for Account {account['Id']}")
        return
    # If safe mode is disabled (default), run all functions concurrently with multithreading.
    # If safe mode is enabled, run all functions sequentially without multithreading.
    if args.safe_mode:
        # AWS APIs requiring a regional client.
        for region in regions:
            get_aws_ec2_instances(region=region['RegionName'], credentials=credentials, account=account)
            get_aws_ecs_resources(region=region['RegionName'], credentials=credentials, account=account)
            get_aws_eks_instances(region=region['RegionName'], credentials=credentials, account=account)
            get_aws_lambda_functions(region=region['RegionName'], credentials=credentials, account=account)
            get_aws_ecs_container_instances(region=region['RegionName'], credentials=credentials, account=account)
            get_aws_ecr_images(region=region['RegionName'], credentials=credentials, account=account)
            if args.data_mode:
                get_aws_rds_instances(region=region['RegionName'], credentials=credentials, account=account)
                get_aws_dynamodb_instances(region=region['RegionName'], credentials=credentials, account=account)
        # S3 APIs using a us-east-1 region.
        if args.data_mode:
            get_aws_s3_buckets(region=select_east_region(), credentials=credentials, account=account)
    else:
        futures = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            # AWS APIs requiring a regional client.
            for region in regions:
                futures.append(executor.submit(get_aws_ec2_instances, region=region['RegionName'], credentials=credentials, account=account))
                futures.append(executor.submit(get_aws_ecs_resources, region=region['RegionName'], credentials=credentials, account=account))
                futures.append(executor.submit(get_aws_eks_instances, region=region['RegionName'], credentials=credentials, account=account))
                futures.append(executor.submit(get_aws_lambda_functions, region=region['RegionName'], credentials=credentials, account=account))
                futures.append(executor.submit(get_aws_ecs_container_instances, region=region['RegionName'], credentials=credentials, account=account))
                futures.append(executor.submit(get_aws_ecr_images, region=region['RegionName'], credentials=credentials, account=account))
                if args.data_mode:
                    futures.append(executor.submit(get_aws_rds_instances, region=region['RegionName'], credentials=credentials, account=account))
                    futures.append(executor.submit(get_aws_dynamodb_instances, region=region['RegionName'], credentials=credentials, account=account))
            # S3 APIs using a us-east-1 region.
            if args.data_mode:
                futures.append(executor.submit(get_aws_s3_buckets, region=select_east_region(), credentials=credentials, account=account))
        for future in concurrent.futures.as_completed(futures):
            if future.exception():
                exceptions += 1
        if exceptions:
            error_print("Exceptions raised during parallel processing: Rerun with '--safe' to debug.")


def count_and_output_results(accounts):
    """ Aggregate and output results """
    vms                       = 0
    container_hosts           = 0
    serverless_containers     = 0
    serverless_functions      = 0
    container_registry_images = 0
    data_buckets              = 0
    data_databases            = 0
    data_warehouses           = 0
    non_os_disks              = 0

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write('Resource,Resource Count,Account Name,Account ID,Region' + '\n')
        for item in totals:
            file.write(','.join(str(x) for x in item) + '\n')
            if item[0] == 'Virtual Machines':
                vms += item[1]
            elif item[0] == 'ECS Container Hosts' or item[0] == 'EKS Container Hosts':
                container_hosts += item[1]
            elif item[0] == 'Serverless Functions':
                serverless_functions += item[1]
            elif item[0] == 'Serverless Containers':
                serverless_containers += item[1]
            elif item[0] == 'Container Registry Images':
                container_registry_images += item[1]
            elif item[0] == 'Data Buckets':
                data_buckets += item[1]
            elif item[0] == 'Cloud-Managed Databases':
                data_databases += item[1]
            elif item[0] == 'Data Warehouses':
                data_warehouses += item[1]
            elif item[0] == 'Non-OS Disks':
                non_os_disks += item[1]

    width = resource_count_column_width
    print(f"\nResults across {len(accounts)} AWS Accounts")
    print(f"- {str(vms).rjust(width)} Virtual Machines")
    print(f"- {str(container_hosts).rjust(width)} Container Hosts")
    print(f"- {str(serverless_functions).rjust(width)} Serverless Functions")
    print(f"- {str(serverless_containers).rjust(width)} Serverless Containers")
    print(f"- {str(container_registry_images).rjust(width)} Container Registry Images")
    if args.data_mode:
        print(f"- {str(data_buckets).rjust(width)} Data Buckets (Public and Private)")
        print(f"- {str(data_databases).rjust(width)} Cloud-Managed Databases (PaaS)")
        print(f"- {str(data_warehouses).rjust(width)} Data Warehouses")
        print(f"- {str(non_os_disks).rjust(width)} Non-OS Disks")
    print(f"\nResults written to {output_file}")


def main():
    """ Calculon Compute! """

    regions = get_aws_regions()

    if args.all:
        print("\nGetting AWS Organization")
        root_account_id, accounts = get_aws_organization()
        if accounts:
            print(f"\nFound {len(accounts)} Accounts in the Organization:")
            for account in accounts:
                print(f"- {account['Id']} {account['Name']} {account['Status']}")
            print('')
        else:
            error_print("Unable to identify accounts in the Organization, getting the current Account.")
            root_account_id, accounts = get_aws_account()
            if root_account_id:
                print(f"\nFound Account:\n- {root_account_id}")
    else:
        print("\nGetting the current AWS Account")
        root_account_id, accounts = get_aws_account()
        if root_account_id:
            print(f"\nFound Account:\n- {root_account_id}")

    print("\nGetting Billable Resources for each AWS Account ...")
    for account in accounts:
        print(f"\nScanning {account['Name']} ...")
        get_aws_resources(regions, account, root_account_id)

    count_and_output_results(accounts)


####

if __name__ == "__main__":
    signal.signal(signal.SIGINT,signal_handler)
    main()
