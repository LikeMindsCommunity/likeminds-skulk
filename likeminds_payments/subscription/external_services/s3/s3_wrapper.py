from ..s3.s3_manager import S3Manager
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from ..logging.logging_wrapper import LoggingWrapper

error_logger = LoggingWrapper.get_instance()
info_logger = LoggingWrapper.get_instance()


class S3Wrapper(S3Manager):

    @staticmethod
    def upload_csv_file(file_name, bucket, csv_object, acl=None):
        s3_resource = boto3.resource(
            's3',
            region_name=settings.S3_BUCKETS.get('media_bucket').get('region'),
            aws_access_key_id=settings.AWS_CREDENTIALS.get('ACCESS_KEY'),
            aws_secret_access_key=settings.AWS_CREDENTIALS.get('SECRET_KEY'))

        ACL = acl
        if ACL is None:
            ACL = 'private'

        try:
            s3_resource.Object(bucket, file_name).put(Body=csv_object.getvalue(), ACL=ACL)

        except ClientError as e:
            error_logger.error(e.args)
            return False
        return True
