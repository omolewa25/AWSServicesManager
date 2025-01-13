import boto3
import logging
from botocore.exceptions import ClientError
import time

from services_handle.logger.loggings import Logger
from services_handle.get_credentials import credentials


class RDSHandler:
    def __init__(self, logger: Logger, region_name: str = 'us-east-1'):
        """
        Initializes the RDSHandler with an AWS RDS client.

        :param logger: Logger instance for logging RDS actions
        :param region_name: AWS region for RDS operations
        """

        creds = credentials()
        self.rds_client = boto3.client(
            "rds",
            aws_access_key_id=creds.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=creds.AWS_SECRET_ACCESS_KEY,
            region_name=creds.AWS_REGION
        )
        self.logger = logger

    # Existing Methods (create, delete, modify, etc.) here...

    def describe_db_parameter_group(self, db_parameter_group_name):
        """
        Retrieve information about a DB parameter group.

        :param db_parameter_group_name: The DB parameter group name
        """
        try:
            response = self.rds_client.describe_db_parameter_groups(DBParameterGroupName=db_parameter_group_name)
            self.logger.info(f"Parameter group details: {response}")
            return response
        except ClientError as e:
            self.logger.error(f"Error describing DB parameter group {db_parameter_group_name}: {e}")
            return None

    def create_db_parameter_group(self, db_parameter_group_name, db_parameter_group_family, description,
                                  parameters=None):
        """
        Create a new DB parameter group.

        :param db_parameter_group_name: The name of the parameter group
        :param db_parameter_group_family: The DB parameter group family (e.g., mysql8.0)
        :param description: A description for the parameter group
        :param parameters: A dictionary of DB parameter key-value pairs (optional)
        """
        try:
            response = self.rds_client.create_db_parameter_group(
                DBParameterGroupName=db_parameter_group_name,
                DBParameterGroupFamily=db_parameter_group_family,
                Description=description
            )
            if parameters:
                self.modify_db_parameter_group(db_parameter_group_name, parameters)
            self.logger.info(f"DB Parameter Group {db_parameter_group_name} created successfully.")
            return response
        except ClientError as e:
            self.logger.error(f"Error creating DB parameter group {db_parameter_group_name}: {e}")
            return None

    def modify_db_parameter_group(self, db_parameter_group_name, parameters):
        """
        Modify the parameters of a DB parameter group.

        :param db_parameter_group_name: The name of the DB parameter group
        :param parameters: A dictionary of DB parameter key-value pairs
        """
        try:
            response = self.rds_client.modify_db_parameter_group(
                DBParameterGroupName=db_parameter_group_name,
                Parameters=[{'ParameterName': key, 'ParameterValue': value, 'ApplyMethod': 'pending-reboot'} for
                            key, value in parameters.items()]
            )
            self.logger.info(f"DB Parameter Group {db_parameter_group_name} modified successfully.")
            return response
        except ClientError as e:
            self.logger.error(f"Error modifying DB parameter group {db_parameter_group_name}: {e}")
            return None

    def delete_db_parameter_group(self, db_parameter_group_name):
        """
        Delete a DB parameter group.

        :param db_parameter_group_name: The name of the DB parameter group
        """
        try:
            response = self.rds_client.delete_db_parameter_group(DBParameterGroupName=db_parameter_group_name)
            self.logger.info(f"DB Parameter Group {db_parameter_group_name} deleted successfully.")
            return response
        except ClientError as e:
            self.logger.error(f"Error deleting DB parameter group {db_parameter_group_name}: {e}")
            return None

    def list_db_clusters(self):
        """
        List all Aurora DB clusters.
        """
        try:
            response = self.rds_client.describe_db_clusters()
            db_clusters = response.get('DBClusters', [])
            for db_cluster in db_clusters:
                self.logger.info(f"Aurora DB Cluster ID: {db_cluster['DBClusterIdentifier']}")
            return db_clusters
        except ClientError as e:
            self.logger.error(f"Error listing DB clusters: {e}")
            return None

    def create_db_cluster_snapshot(self, db_cluster_identifier, snapshot_identifier):
        """
        Create a snapshot of an Aurora DB cluster.

        :param db_cluster_identifier: The DB cluster identifier
        :param snapshot_identifier: The snapshot identifier
        """
        try:
            response = self.rds_client.create_db_cluster_snapshot(
                DBClusterIdentifier=db_cluster_identifier,
                DBClusterSnapshotIdentifier=snapshot_identifier
            )
            self.logger.info(f"Snapshot {snapshot_identifier} created for Aurora DB cluster {db_cluster_identifier}.")
            return response
        except ClientError as e:
            self.logger.error(f"Error creating snapshot for Aurora DB cluster {db_cluster_identifier}: {e}")
            return None

    def restore_db_cluster_from_snapshot(self, db_cluster_identifier, snapshot_identifier):
        """
        Restore an Aurora DB cluster from a snapshot.

        :param db_cluster_identifier: The DB cluster identifier
        :param snapshot_identifier: The snapshot identifier to restore from
        """
        try:
            response = self.rds_client.restore_db_cluster_from_snapshot(
                DBClusterIdentifier=db_cluster_identifier,
                DBSnapshotIdentifier=snapshot_identifier
            )
            self.logger.info(
                f"Restoring Aurora DB cluster {db_cluster_identifier} from snapshot {snapshot_identifier}.")
            return response
        except ClientError as e:
            self.logger.error(
                f"Error restoring Aurora DB cluster {db_cluster_identifier} from snapshot {snapshot_identifier}: {e}")
            return None

    def add_option_group(self, db_instance_identifier, option_group_name):
        """
        Add an option group to an RDS instance.

        :param db_instance_identifier: The DB instance identifier
        :param option_group_name: The option group name
        """
        try:
            response = self.rds_client.modify_db_instance(
                DBInstanceIdentifier=db_instance_identifier,
                OptionGroupName=option_group_name,
                ApplyImmediately=True
            )
            self.logger.info(f"Option group {option_group_name} added to RDS instance {db_instance_identifier}.")
            return response
        except ClientError as e:
            self.logger.error(f"Error adding option group to RDS instance {db_instance_identifier}: {e}")
            return None

    def remove_option_group(self, db_instance_identifier, option_group_name):
        """
        Remove an option group from an RDS instance.

        :param db_instance_identifier: The DB instance identifier
        :param option_group_name: The option group name
        """
        try:
            response = self.rds_client.modify_db_instance(
                DBInstanceIdentifier=db_instance_identifier,
                OptionGroupName=option_group_name,
                ApplyImmediately=True
            )
            self.logger.info(f"Option group {option_group_name} removed from RDS instance {db_instance_identifier}.")
            return response
        except ClientError as e:
            self.logger.error(f"Error removing option group from RDS instance {db_instance_identifier}: {e}")
            return None

    def apply_pending_modifications(self, db_instance_identifier):
        """
        Apply pending modifications to an RDS instance.

        :param db_instance_identifier: The DB instance identifier
        """
        try:
            response = self.rds_client.apply_pending_modifications(DBInstanceIdentifier=db_instance_identifier)
            self.logger.info(f"Pending modifications applied to RDS instance {db_instance_identifier}.")
            return response
        except ClientError as e:
            self.logger.error(f"Error applying pending modifications for RDS instance {db_instance_identifier}: {e}")
            return None

    def enable_multi_az(self, db_instance_identifier):
        """
        Enable Multi-AZ deployment for an RDS instance.

        :param db_instance_identifier: The DB instance identifier
        """
        try:
            response = self.rds_client.modify_db_instance(
                DBInstanceIdentifier=db_instance_identifier,
                MultiAZ=True,
                ApplyImmediately=True
            )
            self.logger.info(f"Multi-AZ deployment enabled for RDS instance {db_instance_identifier}.")
            return response
        except ClientError as e:
            self.logger.error(f"Error enabling Multi-AZ for RDS instance {db_instance_identifier}: {e}")
            return None

    def disable_multi_az(self, db_instance_identifier):
        """
        Disable Multi-AZ deployment for an RDS instance.

        :param db_instance_identifier: The DB instance identifier
        """
        try:
            response = self.rds_client.modify_db_instance(
                DBInstanceIdentifier=db_instance_identifier,
                MultiAZ=False,
                ApplyImmediately=True
            )
            self.logger.info(f"Multi-AZ deployment disabled for RDS instance {db_instance_identifier}.")
            return response
        except ClientError as e:
            self.logger.error(f"Error disabling Multi-AZ for RDS instance {db_instance_identifier}: {e}")
            return None

    def enable_performance_insights(self, db_instance_identifier):
        """
        Enable Performance Insights for an RDS instance.

        :param db_instance_identifier: The DB instance identifier
        """
        try:
            response = self.rds_client.modify_db_instance(
                DBInstanceIdentifier=db_instance_identifier,
                PerformanceInsightsEnabled=True,
                ApplyImmediately=True
            )
            self.logger.info(f"Performance Insights enabled for RDS instance {db_instance_identifier}.")
            return response
        except ClientError as e:
            self.logger.error(f"Error enabling Performance Insights for RDS instance {db_instance_identifier}: {e}")
            return None

    def disable_performance_insights(self, db_instance_identifier):
        """
        Disable Performance Insights for an RDS instance.

        :param db_instance_identifier: The DB instance identifier
        """
        try:
            response = self.rds_client.modify_db_instance(
                DBInstanceIdentifier=db_instance_identifier,
                PerformanceInsightsEnabled=False,
                ApplyImmediately=True
            )
            self.logger.info(f"Performance Insights disabled for RDS instance {db_instance_identifier}.")
            return response
        except ClientError as e:
            self.logger.error(f"Error disabling Performance Insights for RDS instance {db_instance_identifier}: {e}")
            return None

    def describe_event_subscriptions(self, subscription_name=None):
        """
        Retrieve event subscriptions for RDS instance activities.

        :param subscription_name: The subscription name (optional)
        """
        try:
            if subscription_name:
                response = self.rds_client.describe_event_subscriptions(
                    SubscriptionName=subscription_name
                )
            else:
                response = self.rds_client.describe_event_subscriptions()
            self.logger.info(f"Event subscriptions: {response}")
            return response
        except ClientError as e:
            self.logger.error(f"Error describing event subscriptions: {e}")
            return None

    def create_event_subscription(self, subscription_name, source_type, event_categories, sns_topic_arn, enabled=True):
        """
        Create a new event subscription for RDS activity.

        :param subscription_name: The subscription name
        :param source_type: The type of source to receive events (e.g., db-instance)
        :param event_categories: List of event categories (e.g., ['backup', 'failover'])
        :param sns_topic_arn: The ARN of the SNS topic to send notifications
        :param enabled: Whether the subscription is enabled (default: True)
        """
        try:
            response = self.rds_client.create_event_subscription(
                SubscriptionName=subscription_name,
                SourceType=source_type,
                EventCategories=event_categories,
                SnsTopicArn=sns_topic_arn,
                Enabled=enabled
            )
            self.logger.info(f"Event subscription {subscription_name} created successfully.")
            return response
        except ClientError as e:
            self.logger.error(f"Error creating event subscription {subscription_name}: {e}")
            return None

    def delete_event_subscription(self, subscription_name):
        """
        Delete an event subscription.

        :param subscription_name: The subscription name
        """
        try:
            response = self.rds_client.delete_event_subscription(SubscriptionName=subscription_name)
            self.logger.info(f"Event subscription {subscription_name} deleted successfully.")
            return response
        except ClientError as e:
            self.logger.error(f"Error deleting event subscription {subscription_name}: {e}")
            return None


# Example usage
def main():
    logger = logging.getLogger('RDSHandler')
    logging.basicConfig(level=logging.INFO)

    rds_handler = RDSHandler(logger, region_name='us-east-1')

    # Example: Create a new DB Parameter Group
    rds_handler.create_db_parameter_group(
        db_parameter_group_name='custom-parameter-group',
        db_parameter_group_family='mysql8.0',
        description='Custom parameter group for MySQL 8.0',
        parameters={'max_connections': '150'}
    )

    # Example: Enable Performance Insights
    rds_handler.enable_performance_insights(db_instance_identifier='mydbinstance')


if __name__ == "__main__":
    main()
