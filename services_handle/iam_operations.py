import boto3
import logging
from botocore.exceptions import ClientError
import json

from services_handle.get_credentials import credentials
from services_handle.logger.loggings import Logger


class IAMRolePolicyManager:
    def __init__(self, logger: Logger, region_name: str = "us-east-1"):
        """
        Initializes the IAMRolePolicyManager with AWS IAM client.

        :param logger: Logger instance for logging IAM actions
        :param region_name: The AWS region where IAM roles/policies are managed
        """
        creds = credentials()
        self.iam_client = boto3.client(
            "iam",
            aws_access_key_id=creds.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=creds.AWS_SECRET_ACCESS_KEY,
            region_name=creds.AWS_REGION
        )
        self.logger = logger

    def create_iam_role(self, role_name, assume_role_policy_document, description=None, tags=None):
        """
        Create a new IAM role with a trust policy (assume role policy document).

        :param role_name: The name of the IAM role
        :param assume_role_policy_document: The trust policy in JSON format
        :param description: Optional description for the IAM role
        :param tags: Optional tags to attach to the IAM role
        """
        try:
            response = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(assume_role_policy_document),
                Description=description or '',
                Tags=tags or []
            )
            self.logger.info(f"IAM role {role_name} created successfully.")
            return response
        except ClientError as e:
            self.logger.error(f"Error creating IAM role {role_name}: {e}")
            return None

    def delete_iam_role(self, role_name):
        """
        Delete an IAM role.

        :param role_name: The name of the IAM role to delete
        """
        try:
            response = self.iam_client.delete_role(RoleName=role_name)
            self.logger.info(f"IAM role {role_name} deleted successfully.")
            return response
        except ClientError as e:
            self.logger.error(f"Error deleting IAM role {role_name}: {e}")
            return None

    def attach_iam_policy_to_role(self, role_name, policy_arn):
        """
        Attach an IAM policy to an IAM role.

        :param role_name: The name of the IAM role
        :param policy_arn: The ARN of the IAM policy to attach
        """
        try:
            response = self.iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )
            self.logger.info(f"Policy {policy_arn} attached to role {role_name}.")
            return response
        except ClientError as e:
            self.logger.error(f"Error attaching policy {policy_arn} to role {role_name}: {e}")
            return None

    def detach_iam_policy_from_role(self, role_name, policy_arn):
        """
        Detach an IAM policy from an IAM role.

        :param role_name: The name of the IAM role
        :param policy_arn: The ARN of the IAM policy to detach
        """
        try:
            response = self.iam_client.detach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )
            self.logger.info(f"Policy {policy_arn} detached from role {role_name}.")
            return response
        except ClientError as e:
            self.logger.error(f"Error detaching policy {policy_arn} from role {role_name}: {e}")
            return None

    def create_iam_policy(self, policy_name, policy_document, description=None, tags=None):
        """
        Create a new IAM policy with the specified permissions.

        :param policy_name: The name of the IAM policy
        :param policy_document: The policy document in JSON format
        :param description: Optional description for the IAM policy
        :param tags: Optional tags to attach to the IAM policy
        """
        try:
            response = self.iam_client.create_policy(
                PolicyName=policy_name,
                PolicyDocument=json.dumps(policy_document),
                Description=description or '',
                Tags=tags or []
            )
            self.logger.info(f"IAM policy {policy_name} created successfully.")
            return response
        except ClientError as e:
            self.logger.error(f"Error creating IAM policy {policy_name}: {e}")
            return None

    def delete_iam_policy(self, policy_arn):
        """
        Delete an IAM policy.

        :param policy_arn: The ARN of the IAM policy to delete
        """
        try:
            response = self.iam_client.delete_policy(PolicyArn=policy_arn)
            self.logger.info(f"IAM policy {policy_arn} deleted successfully.")
            return response
        except ClientError as e:
            self.logger.error(f"Error deleting IAM policy {policy_arn}: {e}")
            return None

    def list_iam_roles(self):
        """
        List all IAM roles in the account.
        """
        try:
            response = self.iam_client.list_roles()
            roles = response.get('Roles', [])
            if roles:
                for role in roles:
                    self.logger.info(f"Role: {role['RoleName']}")
            else:
                self.logger.info("No IAM roles found.")
            return roles
        except ClientError as e:
            self.logger.error(f"Error listing IAM roles: {e}")
            return None

    def list_iam_policies(self):
        """
        List all IAM policies in the account.
        """
        try:
            response = self.iam_client.list_policies(Scope='All')
            policies = response.get('Policies', [])
            for policy in policies:
                self.logger.info(f"Policy: {policy['PolicyName']} (ARN: {policy['Arn']})")
            return policies
        except ClientError as e:
            self.logger.error(f"Error listing IAM policies: {e}")
            return None

    def get_role(self, role_name):
        """
        Get detailed information about a specific IAM role.

        :param role_name: The name of the IAM role
        """
        try:
            response = self.iam_client.get_role(RoleName=role_name)
            self.logger.info(f"Retrieved details for IAM role {role_name}.")
            return response
        except ClientError as e:
            self.logger.error(f"Error retrieving role {role_name}: {e}")
            return None

    def get_policy(self, policy_arn):
        """
        Get detailed information about a specific IAM policy.

        :param policy_arn: The ARN of the IAM policy
        """
        try:
            response = self.iam_client.get_policy(PolicyArn=policy_arn)
            self.logger.info(f"Retrieved details for IAM policy {policy_arn}.")
            return response
        except ClientError as e:
            self.logger.error(f"Error retrieving policy {policy_arn}: {e}")
            return None

    def assume_role(self, role_arn, session_name, duration_seconds=3600):
        """
        Assume a role and get temporary security credentials.

        :param role_arn: The ARN of the IAM role to assume
        :param session_name: The name of the session
        :param duration_seconds: The duration for which the credentials are valid (default 1 hour)
        """
        try:
            response = self.iam_client.assume_role(
                RoleArn=role_arn,
                RoleSessionName=session_name,
                DurationSeconds=duration_seconds
            )
            self.logger.info(f"Assumed role {role_arn} successfully.")
            return response
        except ClientError as e:
            self.logger.error(f"Error assuming role {role_arn}: {e}")
            return None

    def attach_managed_policy_to_role(self, role_name, managed_policy_arn):
        """
        Attach an AWS managed policy to an IAM role.

        :param role_name: The name of the IAM role
        :param managed_policy_arn: The ARN of the managed IAM policy (e.g., `arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess`)
        """
        try:
            response = self.iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn=managed_policy_arn
            )
            self.logger.info(f"Managed policy {managed_policy_arn} attached to role {role_name}.")
            return response
        except ClientError as e:
            self.logger.error(f"Error attaching managed policy {managed_policy_arn} to role {role_name}: {e}")
            return None

    def create_inline_policy_for_role(self, role_name, policy_name, policy_document):
        """
        Create and attach an inline policy for a specific IAM role.

        :param role_name: The name of the IAM role
        :param policy_name: The name of the inline policy
        :param policy_document: The policy document in JSON format
        """
        try:
            response = self.iam_client.put_role_policy(
                RoleName=role_name,
                PolicyName=policy_name,
                PolicyDocument=json.dumps(policy_document)
            )
            self.logger.info(f"Inline policy {policy_name} created and attached to role {role_name}.")
            return response
        except ClientError as e:
            self.logger.error(f"Error creating inline policy {policy_name} for role {role_name}: {e}")
            return None

    def delete_inline_policy_from_role(self, role_name, policy_name):
        """
        Delete an inline policy from an IAM role.

        :param role_name: The name of the IAM role
        :param policy_name: The name of the inline policy to delete
        """
        try:
            response = self.iam_client.delete_role_policy(
                RoleName=role_name,
                PolicyName=policy_name
            )
            self.logger.info(f"Inline policy {policy_name} deleted from role {role_name}.")
            return response
        except ClientError as e:
            self.logger.error(f"Error deleting inline policy {policy_name} from role {role_name}: {e}")
            return None

    def list_role_tags(self, role_name):
        """
        List tags attached to an IAM role.

        :param role_name: The name of the IAM role
        """
        try:
            response = self.iam_client.list_role_tags(RoleName=role_name)
            tags = response.get('Tags', [])
            for tag in tags:
                self.logger.info(f"Tag - Key: {tag['Key']}, Value: {tag['Value']}")
            return tags
        except ClientError as e:
            self.logger.error(f"Error listing tags for role {role_name}: {e}")
            return None

    def tag_role(self, role_name, tags):
        """
        Add or update tags for an IAM role.

        :param role_name: The name of the IAM role
        :param tags: A list of dictionaries containing 'Key' and 'Value' for each tag
        """
        try:
            response = self.iam_client.tag_role(
                RoleName=role_name,
                Tags=tags
            )
            self.logger.info(f"Tags added/updated for role {role_name}.")
            return response
        except ClientError as e:
            self.logger.error(f"Error adding/updating tags for role {role_name}: {e}")
            return None

    def untag_role(self, role_name, tag_keys):
        """
        Remove tags from an IAM role.

        :param role_name: The name of the IAM role
        :param tag_keys: A list of tag keys to remove
        """
        try:
            response = self.iam_client.untag_role(
                RoleName=role_name,
                TagKeys=tag_keys
            )
            self.logger.info(f"Tags removed from role {role_name}.")
            return response
        except ClientError as e:
            self.logger.error(f"Error removing tags from role {role_name}: {e}")
            return None

    def get_role_trust_relationship(self, role_name):
        """
        Retrieve the trust policy (assume role policy) associated with an IAM role.

        :param role_name: The name of the IAM role
        """
        try:
            response = self.iam_client.get_role(
                RoleName=role_name
            )
            trust_policy = response['Role']['AssumeRolePolicyDocument']
            self.logger.info(f"Trust policy for role {role_name}: {trust_policy}")
            return trust_policy
        except ClientError as e:
            self.logger.error(f"Error retrieving trust policy for role {role_name}: {e}")
            return None

    def generate_policy_simulation_report(self, policy_arn, action, resource):
        """
        Simulate the effect of a policy on a specific action and resource.

        :param policy_arn: The ARN of the IAM policy
        :param action: The AWS action to simulate (e.g., 's3:ListBucket')
        :param resource: The resource to simulate (e.g., 'arn:aws:s3:::my-bucket')
        """
        try:
            response = self.iam_client.simulate_principal_policy(
                PolicySourceArn=policy_arn,
                ActionNames=[action],
                ResourceArns=[resource]
            )
            self.logger.info(f"Policy simulation result for {policy_arn}: {response['EvaluationResults']}")
            return response['EvaluationResults']
        except ClientError as e:
            self.logger.error(f"Error simulating policy {policy_arn}: {e}")
            return None


# Example usage
def main():
    logger = logging.getLogger('IAMRolePolicyManager')
    logging.basicConfig(level=logging.INFO)
    iam_manager = IAMRolePolicyManager(logger, region_name='us-east-1')

    # Example usage of enhanced IAMRolePolicyManager
    role_name = 'example-role'
    policy_name = 'example-policy'
    assume_role_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }

    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "s3:ListBucket",
                "Resource": "arn:aws:s3:::example-bucket"
            }
        ]
    }

    # Create IAM Role
    iam_manager.create_iam_role(role_name, assume_role_policy)

    # Create IAM Policy
    policy_response = iam_manager.create_iam_policy(policy_name, policy_document)

    # Attach IAM Policy to Role
    policy_arn = policy_response['Policy']['Arn']
    iam_manager.attach_iam_policy_to_role(role_name, policy_arn)

    # Simulate policy
    simulation_report = iam_manager.generate_policy_simulation_report(policy_arn, 's3:ListBucket',
                                                                      'arn:aws:s3:::example-bucket')


if __name__ == "__main__":
    main()
