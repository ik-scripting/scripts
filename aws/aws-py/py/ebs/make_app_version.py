#!/usr/bin/env python
'''
  Create Elastic BeanStalk Application environment version.
  Silently Create Application if one not exits.
'''

import json
import os


def __create_storage_location(eb_context):
    bucket_name = eb_context.eb_client.create_storage_location()['S3Bucket']

    print("Using bucket to deploy bundle '{}'".format(bucket_name))
    s3_bucket = eb_context.s3_resource.Bucket(name=bucket_name)
    return bucket_name, s3_bucket


def __create_application_version(eb_context, bucket_info):
    response = eb_context.eb_client.create_application_version(
        ApplicationName=eb_context.application,
        VersionLabel=eb_context.version,
        Description='CI Make application',
        SourceBundle={
            'S3Bucket': bucket_info["bucket_name"],
            'S3Key': bucket_info["key"]
        },
        AutoCreateApplication=False,
        Process=True
    )
    print("Creates an '{}' version '{}'".format(eb_context.application, eb_context.version))
    return response


def __upload_source_bundle(bundled_file, eb_context):
    '''
    Uploading zip file of app version to S3
    '''
    (bucket_name, s3_bucket) = __create_storage_location(eb_context)

    key = eb_context.application + '/' + bundled_file
    print("'{}' Location of the bundle ".format(key))

    s3_bucket.upload_file(bundled_file, key)

    return {
        "key": key,
        "bucket_name": bucket_name
    }


def _delete_existing_version(eb_context):
    eb_context.eb_client.delete_application_version(
        ApplicationName=eb_context.application,
        DeleteSourceBundle=True,
        VersionLabel=eb_context.version,
    )


def _find_existing_version(eb_context):
    response = eb_context.eb_client.describe_application_versions(
        ApplicationName=eb_context.application,
        VersionLabels=[
            eb_context.version
        ],
        MaxRecords=10
    )

    print("Found application versions {} - {}".format(eb_context.application, eb_context.version))

    print(json.dumps(response, indent=4, sort_keys=True, default=str))

    return response['ApplicationVersions']


def make_app_version(bundle_zip_path, eb_context):
    same_version_exists = _find_existing_version(eb_context=eb_context)

    if same_version_exists:
        if eb_context.override_version:
            print("Overriding existing application version by deleting old one and creating a new one with"
                  "the same version.")
            _delete_existing_version(eb_context)
        else:
            print("No need to create application version as it already exists.")
            return

    try:
        bucket_info = __upload_source_bundle(bundled_file=bundle_zip_path, eb_context=eb_context)

        response = __create_application_version(eb_context=eb_context, bucket_info=bucket_info)

        print(json.dumps(response, indent=4, sort_keys=True, default=str))
    finally:
        if bundle_zip_path:
            os.remove(bundle_zip_path)
