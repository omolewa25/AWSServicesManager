#!/usr/bin/env python3

##########################################################
# Created: Omolewa Adaramola, Chinelo                    #
##########################################################

import os
from typing import Union
from datetime import datetime

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("REGION")


# Initialize S3 Client
def get_client(service: str) -> boto3.client:
    """

    :param service: example -> s3, ec2, lambda
    :return: boto3.Session
    """
    return boto3.client(
        service,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )


def upload_file(file_path: str, bucket_name: str, object_name: str = None) -> Union[str, bool]:
    """
    Upload a file to an S3 bucket.

    :param file_path: Local path to the file
    :param bucket_name: The S3 bucket name
    :param object_name: The name of the file in the bucket (if None, the file name will be used)
    :return: True if file was uploaded, else False
    """

    if not object_name:
        object_name = os.path.basename(file_path)

    s3_client = get_client("s3")

    try:
        s3_client.upload_file(file_path, bucket_name, object_name)
        print(f"File uploaded successfully to {bucket_name}/{object_name}")
        return True
    except (NoCredentialsError, PartialCredentialsError):
        return "Credentials are not available or incomplete."
    except Exception as e:
        return f"Error uploading file: {str(e)}"


def download_file(bucket_name, object_name, file_path):
    """
    Download a file from an S3 bucket.

    :param bucket_name: The S3 bucket name
    :param object_name: The name of the file in the bucket
    :param file_path: Local path to save the file
    :return: True if the file was downloaded, else False
    """
    s3_client = get_client("s3")

    try:
        s3_client.download_file(bucket_name, object_name, file_path)
        print(f"File downloaded successfully from {bucket_name}/{object_name} to {file_path}")
        return True
    except Exception as e:
        print(f"Error downloading file: {str(e)}")
    return False


def list_files(bucket_name):
    """
    List all files in an S3 bucket.

    :param bucket_name: The S3 bucket name
    :return: List of files in the bucket
    """
    s3_client = get_client("s3")

    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        files = [obj['Key'] for obj in response.get('Contents', [])]
        return files
    except Exception as e:
        print(f"Error listing files: {str(e)}")
    return []


def delete_file(bucket_name, object_name):
    """
    Delete a file from an S3 bucket.

    :param bucket_name: The S3 bucket name
    :param object_name: The file to delete
    :return: True if the file was deleted, else False
    """
    s3_client = get_client("s3")

    try:
        s3_client.delete_object(Bucket=bucket_name, Key=object_name)
        print(f"File {object_name} deleted from {bucket_name}")
        return True
    except Exception as e:
        print(f"Error deleting file: {str(e)}")
    return False


def create_bucket(bucket_name):
    """
    Create a new S3 bucket.

    :param bucket_name: The name of the bucket to create
    :return: True if the bucket was created, else False
    """
    s3_client = get_client("s3")

    list_of_buckets = s3_client.list_buckets().get("Buckets")

    if bucket_name in [bucket.get("Name") for bucket in list_of_buckets]:

        name = str(datetime.now()).split()[0]
        name = "".join(name.split("-"))
        bucket_name = f"{bucket_name}{name}"

    print(bucket_name)

    try:
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} created successfully.")
        return True
    except Exception as e:
        print(f"Error creating bucket: {str(e)}")
    return False


def delete_bucket(bucket_name):
    """
    Delete an S3 bucket.

    :param bucket_name: The S3 bucket name
    :return: True if the bucket was deleted, else False
    """
    s3_client = get_client("s3")

    try:
        s3_client.delete_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} deleted successfully.")
        return True
    except Exception as e:
        print(f"Error deleting bucket: {str(e)}")
    return False


def get_object_metadata(bucket_name, object_name):
    """
    Get metadata for an object in S3.

    :param bucket_name: The S3 bucket name
    :param object_name: The object in the bucket
    :return: Metadata dictionary or None if error occurred
    """
    s3_client = get_client("s3")

    try:
        response = s3_client.head_object(Bucket=bucket_name, Key=object_name)
        print(f"Metadata for {object_name}: {response}")
        return response
    except Exception as e:
        print(f"Error getting metadata: {str(e)}")
    return None


def copy_object(source_bucket, source_object, destination_bucket, destination_object):
    """
    Copy an object from one S3 bucket to another.

    :param source_bucket: The source bucket name
    :param source_object: The object in the source bucket
    :param destination_bucket: The destination bucket name
    :param destination_object: The name of the object in the destination bucket
    :return: True if the object was copied, else False
    """
    s3_client = get_client("s3")

    try:
        copy_source = {'Bucket': source_bucket, 'Key': source_object}
        s3_client.copy_object(CopySource=copy_source, Bucket=destination_bucket, Key=destination_object)
        print(f"Copied {source_object} from {source_bucket} to {destination_bucket}/{destination_object}")
        return True
    except Exception as e:
        print(f"Error copying object: {str(e)}")
    return False


if __name__ == "__main__":
    create_bucket("omolewa2025")
    delete_bucket("omolewa2025")
    create_bucket("omolewa2025")
    upload_file(file_path="Losss.png", bucket_name="omolewa2025", object_name="projects/dev/esther2026.png")
    delete_file(bucket_name="omolewa2025", object_name="projects/dev/esther2026.png")

