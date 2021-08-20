import abc


class S3Manager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'upload_file') and callable(subclass.upload_file)) or
                NotImplemented)

    @staticmethod
    def upload_csv_file(file_name, bucket, csv_object):
        """
        upload file to s3
        """
        raise NotImplementedError
