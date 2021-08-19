from ..s3.s3_manager import S3Manager
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
import os


class S3Wrapper(S3Manager):

    @staticmethod
    def upload_file(file_name, bucket, object_name=None):
        """Upload a file to an S3 bucket

            :param file_name: File to upload
            :param bucket: Bucket to upload to
            :param object_name: S3 object name. If not specified then file_name is used
            :return: True if file was uploaded, else False
            """

        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = os.path.basename(file_name)

        # Upload the file
        s3_client = boto3.client('s3',
                                 region_name=settings.S3_BUCKETS.get('media_bucket').get('region'),
                                 aws_access_key_id=settings.AWS_CREDENTIALS.get('ACCESS_KEY'),
                                 aws_secret_access_key=settings.AWS_CREDENTIALS.get('SECRET_KEY'))

        try:
            response = s3_client.upload_file(file_name, bucket, object_name)
            print(response)
        except ClientError as e:
            print(e)
            return False
        return True
