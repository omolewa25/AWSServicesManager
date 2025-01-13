#!/usr/bin/env python3

##########################################################
# Created: Omolewa Adaramola, Chinelo                    #
##########################################################

import os

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

from services_handle.logger.loggings import Logger

from services_handle.get_credentials import credentials


class S3Handler:
    def __init__(self, logger: Logger, bucket_name: str):
        """
        Initializes the S3Handler with an S3 client and the specified bucket name.

        :param logger: Logger instance for logging S3 actions
        :param bucket_name: The name of the S3 bucket to interact with
        """
        creds = credentials()
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=creds.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=creds.AWS_SECRET_ACCESS_KEY,
            region_name=creds.AWS_REGION
        )
        self.bucket_name = bucket_name
        self.logger = logger.get_logger()

    def upload_file(self, file_path, object_name=None):
        """
        Uploads a file to the specified S3 bucket.

        :param file_path: The path to the file to upload
        :param object_name: The S3 object name (if None, it uses the file's name)
        """
        if not object_name:
            object_name = os.path.basename(file_path)

        try:
            self.logger.info(f"Uploading {file_path} to s3://{self.bucket_name}/{object_name}")
            self.s3.upload_file(file_path, self.bucket_name, object_name)
            self.logger.info(f"File {object_name} uploaded to s3://{self.bucket_name}")
        except ClientError as e:
            self.logger.error(f"Error uploading file {object_name} to S3: {e}")

    def download_file(self, object_name, download_path):
        """
        Downloads a file from the S3 bucket to the local system.

        :param object_name: The S3 object name
        :param download_path: The local path where the file will be downloaded
        """
        try:
            self.logger.info(f"Downloading {object_name} from s3://{self.bucket_name} to {download_path}")
            self.s3.download_file(self.bucket_name, object_name, download_path)
            self.logger.info(f"File {object_name} downloaded to {download_path}")
        except ClientError as e:
            self.logger.error(f"Error downloading file {object_name} from S3: {e}")

    def list_objects(self):
        """
        Lists all objects in the S3 bucket.
        """
        try:
            self.logger.info(f"Listing objects in s3://{self.bucket_name}")
            response = self.s3.list_objects_v2(Bucket=self.bucket_name)
            if 'Contents' in response:
                for obj in response['Contents']:
                    self.logger.info(f"Object: {obj['Key']} (Last modified: {obj['LastModified']})")
            else:
                self.logger.info(f"No objects found in s3://{self.bucket_name}")
        except ClientError as e:
            self.logger.error(f"Error listing objects in S3: {e}")

    def delete_object(self, object_name):
        """
        Deletes an object from the S3 bucket.

        :param object_name: The name of the object to delete
        """
        try:
            self.logger.info(f"Deleting object {object_name} from s3://{self.bucket_name}")
            self.s3.delete_object(Bucket=self.bucket_name, Key=object_name)
            self.logger.info(f"Object {object_name} deleted from s3://{self.bucket_name}")
        except ClientError as e:
            self.logger.error(f"Error deleting object {object_name} from S3: {e}")

    def check_object_exists(self, object_name):
        """
        Checks if an object exists in the S3 bucket.

        :param object_name: The name of the object to check
        :return: True if the object exists, False otherwise
        """
        try:
            self.logger.info(f"Checking if object {object_name} exists in s3://{self.bucket_name}")
            self.s3.head_object(Bucket=self.bucket_name, Key=object_name)
            self.logger.info(f"Object {object_name} exists in s3://{self.bucket_name}")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                self.logger.warning(f"Object {object_name} not found in s3://{self.bucket_name}")
            else:
                self.logger.error(f"Error checking if object {object_name} exists in S3: {e}")
            return False

    def generate_presigned_url(self, object_name, expiration=3600):
        """
        Generates a pre-signed URL to access an S3 object.

        :param object_name: The name of the S3 object
        :param expiration: The expiration time in seconds (default 1 hour)
        :return: A pre-signed URL
        """
        try:
            self.logger.info(f"Generating pre-signed URL for s3://{self.bucket_name}/{object_name}")
            url = self.s3.generate_presigned_url('get_object',
                                                 Params={'Bucket': self.bucket_name, 'Key': object_name},
                                                 ExpiresIn=expiration)
            self.logger.info(f"Generated pre-signed URL for object {object_name}")
            return url
        except ClientError as e:
            self.logger.error(f"Error generating pre-signed URL for {object_name}: {e}")
            return None

    def create_bucket(self, bucket_name):
        """
        Creates a new S3 bucket.

        :param bucket_name: The name of the bucket to create
        """
        try:
            self.logger.info(f"Creating S3 bucket {bucket_name}")
            self.s3.create_bucket(Bucket=bucket_name)
            self.logger.info(f"S3 bucket {bucket_name} created successfully.")
        except ClientError as e:
            self.logger.error(f"Error creating S3 bucket {bucket_name}: {e}")

    def delete_bucket(self):
        """
        Deletes an empty S3 bucket.
        """
        try:
            self.logger.info(f"Deleting S3 bucket {self.bucket_name}")
            self.s3.delete_bucket(Bucket=self.bucket_name)
            self.logger.info(f"S3 bucket {self.bucket_name} deleted successfully.")
        except ClientError as e:
            self.logger.error(f"Error deleting S3 bucket {self.bucket_name}: {e}")

    # --- New Functionalities ---
    def copy_object(self, source_bucket, source_object, destination_object):
        """
        Copy an object from one S3 location to another.

        :param source_bucket: The source S3 bucket
        :param source_object: The source object key
        :param destination_object: The destination object key
        """
        try:
            self.logger.info(
                f"Copying object from s3://{source_bucket}/{source_object} to s3://{self.bucket_name}/{destination_object}")
            self.s3.copy_object(Bucket=self.bucket_name,
                                CopySource={'Bucket': source_bucket, 'Key': source_object},
                                Key=destination_object)
            self.logger.info(f"Object copied to s3://{self.bucket_name}/{destination_object}")
        except ClientError as e:
            self.logger.error(
                f"Error copying object from s3://{source_bucket}/{source_object} to s3://{self.bucket_name}/{destination_object}: {e}")

    def move_object(self, source_bucket, source_object, destination_object):
        """
        Move an object (copy and then delete original).

        :param source_bucket: The source S3 bucket
        :param source_object: The source object key
        :param destination_object: The destination object key
        """
        self.copy_object(source_bucket, source_object, destination_object)
        self.delete_object(source_object)

    def list_objects_by_prefix(self, prefix):
        """
        List objects in the bucket by prefix (like a folder).

        :param prefix: The prefix to filter by (like "folder/")
        """
        try:
            self.logger.info(f"Listing objects with prefix '{prefix}' in s3://{self.bucket_name}")
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            if 'Contents' in response:
                for obj in response['Contents']:
                    self.logger.info(f"Object: {obj['Key']} (Last modified: {obj['LastModified']})")
            else:
                self.logger.info(f"No objects found with prefix '{prefix}' in s3://{self.bucket_name}")
        except ClientError as e:
            self.logger.error(f"Error listing objects by prefix in S3: {e}")

    def set_object_acl(self, object_name, acl):
        """
        Set ACL (Access Control List) for an object.

        :param object_name: The object name
        :param acl: The ACL to set (e.g., 'private', 'public-read')
        """
        try:
            self.logger.info(f"Setting ACL {acl} for object {object_name}")
            self.s3.put_object_acl(Bucket=self.bucket_name, Key=object_name, ACL=acl)
            self.logger.info(f"ACL set to {acl} for object {object_name}")
        except ClientError as e:
            self.logger.error(f"Error setting ACL for object {object_name}: {e}")

    def get_object_metadata(self, object_name):
        """
        Retrieve metadata for an object (e.g., size, content-type, etc.).

        :param object_name: The name of the object
        :return: Metadata dictionary or None if not found
        """
        try:
            self.logger.info(f"Getting metadata for object {object_name}")
            metadata = self.s3.head_object(Bucket=self.bucket_name, Key=object_name)
            self.logger.info(f"Metadata for {object_name}: {metadata}")
            return metadata
        except ClientError as e:
            self.logger.error(f"Error retrieving metadata for object {object_name}: {e}")
            return None

    def enable_versioning(self):
        """
        Enable versioning for the S3 bucket.
        """
        try:
            self.logger.info(f"Enabling versioning for bucket {self.bucket_name}")
            self.s3.put_bucket_versioning(Bucket=self.bucket_name,
                                          VersioningConfiguration={'Status': 'Enabled'})
            self.logger.info(f"Versioning enabled for bucket {self.bucket_name}")
        except ClientError as e:
            self.logger.error(f"Error enabling versioning for bucket {self.bucket_name}: {e}")

    def disable_versioning(self):
        """
        Disable versioning for the S3 bucket.
        """
        try:
            self.logger.info(f"Disabling versioning for bucket {self.bucket_name}")
            self.s3.put_bucket_versioning(Bucket=self.bucket_name,
                                          VersioningConfiguration={'Status': 'Suspended'})
            self.logger.info(f"Versioning disabled for bucket {self.bucket_name}")
        except ClientError as e:
            self.logger.error(f"Error disabling versioning for bucket {self.bucket_name}: {e}")

    def restore_archived_object(self, object_name):
        """
        Restore an archived object (from Glacier) to standard storage class.

        :param object_name: The name of the object to restore
        """
        try:
            self.logger.info(f"Restoring archived object {object_name}")
            self.s3.restore_object(Bucket=self.bucket_name, Key=object_name,
                                   RestoreRequest={'Days': 1, 'GlacierJobParameters': {'Tier': 'Standard'}})
            self.logger.info(f"Object {object_name} restore requested.")
        except ClientError as e:
            self.logger.error(f"Error restoring archived object {object_name}: {e}")

    def set_bucket_cors_policy(self, cors_rules):
        """
        Set a CORS (Cross-Origin Resource Sharing) policy for the bucket.

        :param cors_rules: The CORS configuration rules
        """
        try:
            self.logger.info(f"Setting CORS policy for bucket {self.bucket_name}")
            self.s3.put_bucket_cors(Bucket=self.bucket_name, CORSConfiguration={'CORSRules': cors_rules})
            self.logger.info(f"CORS policy set for bucket {self.bucket_name}")
        except ClientError as e:
            self.logger.error(f"Error setting CORS policy for bucket {self.bucket_name}: {e}")

    def get_bucket_encryption(self):
        """
        Retrieve the encryption configuration for the bucket.
        """
        try:
            self.logger.info(f"Getting encryption configuration for bucket {self.bucket_name}")
            encryption = self.s3.get_bucket_encryption(Bucket=self.bucket_name)
            self.logger.info(f"Encryption configuration for bucket {self.bucket_name}: {encryption}")
            return encryption
        except ClientError as e:
            self.logger.error(f"Error retrieving encryption configuration for bucket {self.bucket_name}: {e}")
            return None


# Example usage:
def main():
    bucket_name = 'your-s3-bucket-name'
    logger = Logger(bucket_name, log_prefix='myapp/', aws_region='us-east-1')

    # Instantiate the S3Handler
    s3_handler = S3Handler(logger, bucket_name)

    # Use new functionalities:
    s3_handler.copy_object('source-bucket', 'source-object.txt', 'destination-object.txt')
    s3_handler.move_object('source-bucket', 'source-object.txt', 'destination-folder/destination-object.txt')
    s3_handler.set_object_acl('object.txt', 'public-read')
    metadata = s3_handler.get_object_metadata('object.txt')
    print(metadata)
    s3_handler.enable_versioning()
    s3_handler.set_bucket_cors_policy([{
        'AllowedOrigins': ['*'],
        'AllowedMethods': ['GET', 'POST'],
        'AllowedHeaders': ['*']
    }])

if __name__ == "__main__":
    main()
