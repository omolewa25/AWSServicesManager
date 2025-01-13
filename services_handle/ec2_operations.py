import boto3
from botocore.exceptions import ClientError
from datetime import datetime

from services_handle.logger.loggings import Logger
from services_handle.get_credentials import credentials


class EC2Handler:
    def __init__(self, logger: Logger):
        """
        Initialize the EC2Handler with an AWS EC2 client and a logger instance.

        :param logger: An instance of the Logger class for logging EC2 actions
        """
        creds = credentials()
        self.ec2 = boto3.client(
            "ec2",
            aws_access_key_id=creds.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=creds.AWS_SECRET_ACCESS_KEY,
            region_name=creds.AWS_REGION
        )
        self.ec2 = boto3.client('ec2')
        self.logger = logger.get_logger()

    def create_instance(self, ami_id, instance_type, key_name, security_group_ids=None, min_count=1, max_count=1,
                        tags=None):
        try:
            self.logger.info(f"Creating EC2 instance: {ami_id}, {instance_type}, KeyPair: {key_name}")
            response = self.ec2.run_instances(
                ImageId=ami_id,
                InstanceType=instance_type,
                MinCount=min_count,
                MaxCount=max_count,
                KeyName=key_name,
                SecurityGroupIds=security_group_ids,
                TagSpecifications=[{
                    'ResourceType': 'instance',
                    'Tags': tags or []
                }] if tags else []
            )
            instance_id = response['Instances'][0]['InstanceId']
            self.logger.info(f"Instance {instance_id} created.")
            return instance_id
        except ClientError as e:
            self.logger.error(f"Error creating EC2 instance: {e}")
            return None

    def stop_instance(self, instance_id):
        try:
            self.logger.info(f"Stopping EC2 instance {instance_id}")
            response = self.ec2.stop_instances(InstanceIds=[instance_id])
            self.logger.info(
                f"Stopping Instance {instance_id}. Current state: {response['StoppingInstances'][0]['CurrentState']['Name']}")
        except ClientError as e:
            self.logger.error(f"Error stopping EC2 instance {instance_id}: {e}")

    def start_instance(self, instance_id):
        try:
            self.logger.info(f"Starting EC2 instance {instance_id}")
            response = self.ec2.start_instances(InstanceIds=[instance_id])
            self.logger.info(
                f"Starting Instance {instance_id}. Current state: {response['StartingInstances'][0]['CurrentState']['Name']}")
        except ClientError as e:
            self.logger.error(f"Error starting EC2 instance {instance_id}: {e}")

    def reboot_instance(self, instance_id):
        """
        Reboot an EC2 instance.
        """
        try:
            self.logger.info(f"Rebooting EC2 instance {instance_id}")
            response = self.ec2.reboot_instances(InstanceIds=[instance_id])
            self.logger.info(f"Instance {instance_id} has been rebooted.")
        except ClientError as e:
            self.logger.error(f"Error rebooting EC2 instance {instance_id}: {e}")

    def terminate_instance(self, instance_id):
        try:
            self.logger.info(f"Terminating EC2 instance {instance_id}")
            response = self.ec2.terminate_instances(InstanceIds=[instance_id])
            self.logger.info(
                f"Terminating Instance {instance_id}. Current state: {response['TerminatingInstances'][0]['CurrentState']['Name']}")
        except ClientError as e:
            self.logger.error(f"Error terminating EC2 instance {instance_id}: {e}")

    def describe_instance(self, instance_id):
        """
        Describe an EC2 instance and return detailed information.
        """
        try:
            self.logger.info(f"Describing EC2 instance {instance_id}")
            response = self.ec2.describe_instances(InstanceIds=[instance_id])
            instance_details = response['Reservations'][0]['Instances'][0]
            self.logger.info(f"Instance {instance_id} details: {instance_details}")
            return instance_details
        except ClientError as e:
            self.logger.error(f"Error describing EC2 instance {instance_id}: {e}")
            return None

    def get_instance_status(self, instance_id):
        """
        Get the status of a specific EC2 instance (running, stopped, etc.)
        """
        try:
            self.logger.info(f"Getting status of EC2 instance {instance_id}")
            response = self.ec2.describe_instance_status(InstanceIds=[instance_id])
            if response['InstanceStatuses']:
                status = response['InstanceStatuses'][0]['InstanceState']['Name']
                self.logger.info(f"Instance {instance_id} is in state: {status}.")
                return status
            else:
                self.logger.warning(f"Instance {instance_id} does not have any status information.")
                return 'No status info available'
        except ClientError as e:
            self.logger.error(f"Error getting status of EC2 instance {instance_id}: {e}")
            return None

    def create_ami(self, instance_id, name, description='Created from EC2Handler'):
        """
        Create an AMI from an EC2 instance.
        """
        try:
            self.logger.info(f"Creating AMI from EC2 instance {instance_id}, AMI name: {name}")
            response = self.ec2.create_image(
                InstanceId=instance_id,
                Name=name,
                Description=description,
                NoReboot=True
            )
            ami_id = response['ImageId']
            self.logger.info(f"AMI {ami_id} created from instance {instance_id}.")
            return ami_id
        except ClientError as e:
            self.logger.error(f"Error creating AMI from EC2 instance {instance_id}: {e}")
            return None

    def modify_instance_type(self, instance_id, new_instance_type):
        """
        Modify the instance type of a running EC2 instance.
        """
        try:
            self.logger.info(f"Modifying instance {instance_id} to new type {new_instance_type}")
            response = self.ec2.modify_instance_attribute(
                InstanceId=instance_id,
                InstanceType={'Value': new_instance_type}
            )
            self.logger.info(f"Instance {instance_id} type modified to {new_instance_type}.")
        except ClientError as e:
            self.logger.error(f"Error modifying instance type for {instance_id}: {e}")

    def attach_volume(self, instance_id, volume_id, device):
        """
        Attach an EBS volume to an EC2 instance.
        """
        try:
            self.logger.info(f"Attaching volume {volume_id} to instance {instance_id} on device {device}")
            response = self.ec2.attach_volume(
                InstanceId=instance_id,
                VolumeId=volume_id,
                Device=device
            )
            self.logger.info(f"Volume {volume_id} attached to instance {instance_id} on device {device}.")
        except ClientError as e:
            self.logger.error(f"Error attaching volume {volume_id} to instance {instance_id}: {e}")

    def detach_volume(self, instance_id, volume_id):
        """
        Detach an EBS volume from an EC2 instance.
        """
        try:
            self.logger.info(f"Detaching volume {volume_id} from instance {instance_id}")
            response = self.ec2.detach_volume(
                InstanceId=instance_id,
                VolumeId=volume_id
            )
            self.logger.info(f"Volume {volume_id} detached from instance {instance_id}.")
        except ClientError as e:
            self.logger.error(f"Error detaching volume {volume_id} from instance {instance_id}: {e}")

    def create_key_pair(self, key_name):
        """
        Create a new EC2 key pair.
        """
        try:
            self.logger.info(f"Creating EC2 key pair {key_name}")
            response = self.ec2.create_key_pair(KeyName=key_name)
            self.logger.info(f"Key pair {key_name} created.")
            return response['KeyMaterial']
        except ClientError as e:
            self.logger.error(f"Error creating key pair {key_name}: {e}")
            return None

    def delete_key_pair(self, key_name):
        """
        Delete an EC2 key pair.
        """
        try:
            self.logger.info(f"Deleting EC2 key pair {key_name}")
            self.ec2.delete_key_pair(KeyName=key_name)
            self.logger.info(f"Key pair {key_name} deleted.")
        except ClientError as e:
            self.logger.error(f"Error deleting key pair {key_name}: {e}")

    def describe_key_pairs(self):
        """
        Describe all EC2 key pairs in the account.
        """
        try:
            self.logger.info("Describing EC2 key pairs")
            response = self.ec2.describe_key_pairs()
            key_pairs = response['KeyPairs']
            if key_pairs:
                for key in key_pairs:
                    self.logger.info(f"Key Name: {key['KeyName']}, Key Fingerprint: {key['KeyFingerprint']}")
            else:
                self.logger.warning("No key pairs found.")
            return key_pairs
        except ClientError as e:
            self.logger.error(f"Error describing EC2 key pairs: {e}")
            return []


# Example usage
def main():
    # Replace with your actual S3 bucket name
    bucket_name = 'your-s3-bucket-name'

    # Create logger instance for S3 logging
    logger = Logger(bucket_name, log_prefix='myapp/', aws_region='us-east-1')

    # Create EC2Handler with the logger
    ec2_handler = EC2Handler(logger)

    # Example EC2 operations
    instance_id = ec2_handler.create_instance('ami-0c55b159cbfafe1f0', 't2.micro', 'your-key-name')
    if instance_id:
        ec2_handler.get_instance_status(instance_id)
        ec2_handler.start_instance(instance_id)
        ec2_handler.stop_instance(instance_id)
        ec2_handler.reboot_instance(instance_id)
        ec2_handler.terminate_instance(instance_id)


if __name__ == "__main__":
    main()
