import os

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY_ID", "PxGs5b1Rv4oA7Ig0xGoY")
AWS_SECRET_ACCESS_KEY = os.getenv("S3_SECRET_ACCESS_KEY", "VnwammFFZlllBwIpoFBMNZt19tlbGMjoQz7U3Tem")
AWS_STORAGE_BUCKET_NAME = os.getenv("S3_STORAGE_BUCKET_NAME", 'accident-detect')
AWS_S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "http://localhost:9000/")
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = True
AWS_S3_FILE_OVERWRITE = False
