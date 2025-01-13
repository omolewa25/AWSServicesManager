import boto3
import json
import time
from botocore.exceptions import ClientError

from services_handle.s3_operations import Logger
from services_handle.get_credentials import credentials


class LambdaFunctionManager:
    def __init__(self, logger: Logger, region_name: str = "us-east-1"):
        """
        Initializes the LambdaFunctionManager with AWS Lambda client.

        :param logger: Logger instance for logging Lambda actions
        :param region_name: The AWS region where the Lambda function resides
        """
        creds = credentials()
        self.lambda_client = boto3.client(
            "lambda",
            aws_access_key_id=creds.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=creds.AWS_SECRET_ACCESS_KEY,
            region_name=creds.AWS_REGION
        )
        self.logger = logger

    def create_lambda_function(self, function_name, role_arn, handler, zip_file_path, memory_size=128, timeout=3):
        """
        Create a new Lambda function.
        """
        try:
            with open(zip_file_path, 'rb') as zip_file:
                zip_content = zip_file.read()

            response = self.lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.8',
                Role=role_arn,
                Handler=handler,
                Code={'ZipFile': zip_content},
                MemorySize=memory_size,
                Timeout=timeout,
                Publish=True
            )
            self.logger.info(f"Lambda function {function_name} created successfully.")
            return response
        except ClientError as e:
            self.logger.error(f"Error creating Lambda function {function_name}: {e}")
            return None

    def update_lambda_function_code(self, function_name, zip_file_path):
        """
        Update the code of an existing Lambda function.
        """
        try:
            with open(zip_file_path, 'rb') as zip_file:
                zip_content = zip_file.read()

            response = self.lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_content,
                Publish=True
            )
            self.logger.info(f"Lambda function {function_name} updated successfully.")
            return response
        except ClientError as e:
            self.logger.error(f"Error updating Lambda function {function_name}: {e}")
            return None

    def invoke_lambda_function(self, function_name, payload=None, invocation_type="RequestResponse"):
        """
        Invoke a Lambda function synchronously or asynchronously.
        """
        try:
            response = self.lambda_client.invoke(
                FunctionName=function_name,
                InvocationType=invocation_type,
                Payload=json.dumps(payload) if payload else '{}'
            )
            response_payload = json.loads(response['Payload'].read())
            self.logger.info(f"Lambda function {function_name} invoked successfully. Response: {response_payload}")
            return response_payload
        except ClientError as e:
            self.logger.error(f"Error invoking Lambda function {function_name}: {e}")
            return None

    def delete_lambda_function(self, function_name):
        """
        Delete an existing Lambda function.
        """
        try:
            response = self.lambda_client.delete_function(FunctionName=function_name)
            self.logger.info(f"Lambda function {function_name} deleted successfully.")
            return response
        except ClientError as e:
            self.logger.error(f"Error deleting Lambda function {function_name}: {e}")
            return None

    def get_lambda_function_configuration(self, function_name):
        """
        Get configuration details of a Lambda function.
        """
        try:
            response = self.lambda_client.get_function_configuration(FunctionName=function_name)
            self.logger.info(f"Lambda function {function_name} configuration retrieved successfully.")
            return response
        except ClientError as e:
            self.logger.error(f"Error retrieving configuration for Lambda function {function_name}: {e}")
            return None

    def list_lambda_functions(self):
        """
        List all Lambda functions in the current AWS region.
        """
        try:
            response = self.lambda_client.list_functions()
            functions = response.get('Functions', [])
            if functions:
                for func in functions:
                    self.logger.info(f"Lambda Function: {func['FunctionName']} (Runtime: {func['Runtime']})")
            else:
                self.logger.info("No Lambda functions found.")
            return functions
        except ClientError as e:
            self.logger.error(f"Error listing Lambda functions: {e}")
            return None

    def update_lambda_function_configuration(self, function_name, memory_size=None, timeout=None):
        """
        Update the configuration (memory size, timeout) of an existing Lambda function.
        """
        try:
            update_params = {}
            if memory_size is not None:
                update_params['MemorySize'] = memory_size
            if timeout is not None:
                update_params['Timeout'] = timeout

            if update_params:
                response = self.lambda_client.update_function_configuration(
                    FunctionName=function_name,
                    **update_params
                )
                self.logger.info(f"Lambda function {function_name} configuration updated successfully.")
                return response
            else:
                self.logger.info(f"No updates provided for Lambda function {function_name}.")
                return None
        except ClientError as e:
            self.logger.error(f"Error updating configuration for Lambda function {function_name}: {e}")
            return None

    def get_lambda_function_logs(self, function_name, start_time=None, end_time=None, limit=100):
        """
        Retrieve CloudWatch logs for a specific Lambda function.
        """
        try:
            log_group = f"/aws/lambda/{function_name}"
            logs_client = boto3.client('logs', region_name=self.lambda_client.meta.region_name)

            filter_params = {
                'logGroupName': log_group,
                'limit': limit,
                'startTime': start_time or int(time.time() * 1000) - 86400000,  # Default to last 24 hours
                'endTime': end_time or int(time.time() * 1000)
            }

            log_streams = logs_client.filter_log_events(**filter_params)
            logs = log_streams.get('events', [])
            for log in logs:
                self.logger.info(f"Log Event: {log['message']}")

            return logs
        except ClientError as e:
            self.logger.error(f"Error retrieving logs for Lambda function {function_name}: {e}")
            return None

    def create_event_source_mapping(self, function_name, event_source_arn, batch_size=100):
        """
        Create an event source mapping to trigger a Lambda function.
        """
        try:
            response = self.lambda_client.create_event_source_mapping(
                EventSourceArn=event_source_arn,
                FunctionName=function_name,
                BatchSize=batch_size
            )
            self.logger.info(f"Event source mapping created for {function_name} with ARN {event_source_arn}.")
            return response
        except ClientError as e:
            self.logger.error(f"Error creating event source mapping for Lambda function {function_name}: {e}")
            return None

    def add_layer_to_lambda(self, function_name, layer_arn):
        """
        Add a layer to the Lambda function.
        """
        try:
            response = self.lambda_client.update_function_configuration(
                FunctionName=function_name,
                Layers=[layer_arn]
            )
            self.logger.info(f"Layer {layer_arn} added to Lambda function {function_name}.")
            return response
        except ClientError as e:
            self.logger.error(f"Error adding layer to Lambda function {function_name}: {e}")
            return None

    def publish_lambda_function_version(self, function_name):
        """
        Publish a new version of the Lambda function.
        """
        try:
            response = self.lambda_client.publish_version(FunctionName=function_name)
            self.logger.info(f"Lambda function {function_name} version published successfully.")
            return response
        except ClientError as e:
            self.logger.error(f"Error publishing version for Lambda function {function_name}: {e}")
            return None

    def get_lambda_function_versions(self, function_name):
        """
        List all versions of a Lambda function.
        """
        try:
            response = self.lambda_client.list_versions_by_function(FunctionName=function_name)
            versions = response.get('Versions', [])
            for version in versions:
                self.logger.info(f"Lambda Function Version: {version['Version']}")
            return versions
        except ClientError as e:
            self.logger.error(f"Error retrieving versions for Lambda function {function_name}: {e}")
            return None

    def delete_lambda_function_version(self, function_name, version):
        """
        Delete a specific version of a Lambda function.
        """
        try:
            response = self.lambda_client.delete_function(
                FunctionName=function_name,
                Qualifier=version
            )
            self.logger.info(f"Lambda function version {version} deleted successfully.")
            return response
        except ClientError as e:
            self.logger.error(f"Error deleting version {version} for Lambda function {function_name}: {e}")
            return None

    def create_lambda_alias(self, function_name, alias_name, function_version):
        """
        Create an alias for a Lambda function.
        """
        try:
            response = self.lambda_client.create_alias(
                FunctionName=function_name,
                Name=alias_name,
                FunctionVersion=function_version
            )
            self.logger.info(f"Alias {alias_name} created for Lambda function {function_name}.")
            return response
        except ClientError as e:
            self.logger.error(f"Error creating alias for Lambda function {function_name}: {e}")
            return None

    def get_lambda_alias(self, function_name, alias_name):
        """
        Get an alias for a Lambda function.
        """
        try:
            response = self.lambda_client.get_alias(
                FunctionName=function_name,
                Name=alias_name
            )
            self.logger.info(f"Lambda function alias {alias_name} retrieved successfully.")
            return response
        except ClientError as e:
            self.logger.error(f"Error retrieving alias {alias_name} for Lambda function {function_name}: {e}")
            return None

    def delete_lambda_alias(self, function_name, alias_name):
        """
        Delete a specific alias for a Lambda function.
        """
        try:
            response = self.lambda_client.delete_alias(
                FunctionName=function_name,
                Name=alias_name
            )
            self.logger.info(f"Alias {alias_name} deleted for Lambda function {function_name}.")
            return response
        except ClientError as e:
            self.logger.error(f"Error deleting alias {alias_name} for Lambda function {function_name}: {e}")
            return None


# Example usage
def main():
    logger = logging.getLogger('LambdaManager')
    logging.basicConfig(level=logging.INFO)
    lambda_manager = LambdaFunctionManager(logger, region_name='us-east-1')

    # Example usage of extended LambdaFunctionManager
    function_name = 'example-lambda-function'
    role_arn = 'arn:aws:iam::account-id:role/lambda-execution-role'
    handler = 'lambda_function.lambda_handler'
    zip_file_path = 'path/to/your/lambda.zip'

    # Create Lambda function
    lambda_manager.create_lambda_function(function_name, role_arn, handler, zip_file_path)

    # Update Lambda function configuration
    lambda_manager.update_lambda_function_configuration(function_name, memory_size=256, timeout=5)

    # Get Lambda function logs
    lambda_manager.get_lambda_function_logs(function_name)

    # Add Layer to Lambda function
    lambda_manager.add_layer_to_lambda(function_name, 'arn:aws:lambda:us-east-1:123456789012:layer:my-layer:1')

    # Publish Lambda function version
    lambda_manager.publish_lambda_function_version(function_name)

    # Get all versions of Lambda function
    lambda_manager.get_lambda_function_versions(function_name)

    # Delete Lambda function version
    lambda_manager.delete_lambda_function_version(function_name, '1')


if __name__ == "__main__":
    main()
