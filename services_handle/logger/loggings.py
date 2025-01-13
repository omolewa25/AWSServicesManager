import logging
import boto3
from logging import Handler
from botocore.exceptions import ClientError
from datetime import datetime


class S3LogHandler(Handler):
    def __init__(self, bucket_name, log_prefix='logs/', aws_region='us-east-1'):
        """
        Initialize the S3Handler to upload logs to an S3 bucket.

        :param bucket_name: Name of the S3 bucket where logs will be uploaded.
        :param log_prefix: Prefix for the log file name (optional, defaults to 'logs/').
        :param aws_region: The AWS region where the S3 bucket is located.
        """
        super().__init__()
        self.bucket_name = bucket_name
        self.log_prefix = log_prefix
        self.aws_region = aws_region
        self.s3_client = boto3.client('s3', region_name=self.aws_region)
        self.log_buffer = []

    def emit(self, record):
        """
        Emit the log record to the S3 bucket.
        """
        try:
            log_message = self.format(record)
            # Append the log message to the buffer
            self.log_buffer.append(log_message)

            # If the buffer reaches a certain size (e.g., 10 messages), upload it to S3
            if len(self.log_buffer) >= 10:
                self._upload_to_s3()
        except Exception as e:
            print(f"Failed to write log to S3: {e}")

    def _upload_to_s3(self):
        """
        Upload the logs in the buffer to S3 as a new file.
        """
        try:
            # Generate a log file name with a timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            log_file_name = f"{self.log_prefix}log_{timestamp}.txt"
            log_content = "\n".join(self.log_buffer)

            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=log_file_name,
                Body=log_content
            )

            print(f"Logs successfully uploaded to S3: s3://{self.bucket_name}/{log_file_name}")

            # Clear the buffer after uploading
            self.log_buffer = []
        except ClientError as e:
            print(f"Failed to upload logs to S3: {e}")
        except Exception as e:
            print(f"Unexpected error during S3 upload: {e}")


class Logger:
    def __init__(self, bucket_name, log_prefix='logs/', aws_region='us-east-1', log_level=logging.DEBUG):
        """
        Initializes the logger with an S3Handler.

        :param bucket_name: Name of the S3 bucket where logs will be uploaded.
        :param log_prefix: Prefix for the log file name (optional, defaults to 'logs/').
        :param aws_region: The AWS region where the S3 bucket is located.
        :param log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)

        # Create a formatter
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(log_format)

        # Create an S3 handler to send logs to S3
        s3_handler = S3LogHandler(bucket_name, log_prefix, aws_region)
        s3_handler.setFormatter(formatter)

        # Add the S3 handler to the logger
        self.logger.addHandler(s3_handler)

    def get_logger(self):
        """
        Returns the logger instance.
        """
        return self.logger

    def log_debug(self, message):
        self.logger.debug(message)

    def log_info(self, message):
        self.logger.info(message)

    def log_warning(self, message):
        self.logger.warning(message)

    def log_error(self, message):
        self.logger.error(message)

    def log_exception(self, exception):
        """
        Log exception with traceback details.
        :param exception: The exception instance
        """
        self.logger.exception(exception)

    def log_critical(self, message):
        self.logger.critical(message)


# Example usage
def main():
    # Replace with your actual S3 bucket name
    bucket_name = 'your-s3-bucket-name'

    # Create logger instance for S3 logging
    logger = Logger(bucket_name, log_prefix='myapp/', aws_region='us-east-1')

    # Get the logger
    log = logger.get_logger()

    # Log some messages
    log.debug("This is a debug message")
    log.info("This is an info message")
    log.warning("This is a warning message")
    log.error("This is an error message")
    log.critical("This is a critical message")


if __name__ == "__main__":
    main()
