from storages.backends.s3boto3 import S3Boto3Storage
 
class CustomS3Storage(S3Boto3Storage):
    location = 'regplus_document'
    file_overwrite = False