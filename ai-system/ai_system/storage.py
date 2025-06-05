import os

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

S3_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY_ID", "PxGs5b1Rv4oA7Ig0xGoY")
S3_SECRET_ACCESS_KEY = os.getenv("S3_SECRET_ACCESS_KEY", "VnwammFFZlllBwIpoFBMNZt19tlbGMjoQz7U3Tem")
S3_STORAGE_BUCKET_NAME = os.getenv("S3_STORAGE_BUCKET_NAME", 'accident-detect')
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "http://localhost:9001/")