from ..s3.s3_manager import S3Manager
import boto3
import pandas as pd
from io import StringIO
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

    @staticmethod
    def upload_csv_file_and_get_link(pd_dataframe: pd.DataFrame, dir_path: str, file_name: str):

        csv_buffer = StringIO()
        pd_dataframe.to_csv(csv_buffer)

        file_path = '{}/{}'.format(dir_path, file_name)
        bucket = settings.S3_BUCKETS.get('media_bucket').get('name')

        upload_status = S3Wrapper.upload_csv_file(file_path, bucket, csv_buffer, acl='public-read')

        if upload_status:
            return {'link': 'https://{}.s3.amazonaws.com/{}'.format(bucket, file_path)}

        return {'error_message': 'error while uploading csv file'}
