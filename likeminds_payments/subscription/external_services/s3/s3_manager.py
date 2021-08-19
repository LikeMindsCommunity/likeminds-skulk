import abc


class S3Manager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'upload_file') and callable(subclass.upload_file)) or
                NotImplemented)

    @staticmethod
    def upload_file(file_name, bucket, object_name=None):
        """
        upload file to s3
        """
        raise NotImplementedError
