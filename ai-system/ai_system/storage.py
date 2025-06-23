import os

try:
    from botocore.config import Config
except Exception as e:
    pass
else:
    AWS_S3_CLIENT_CONFIG = Config(
        max_pool_connections=int(os.getenv('AWS_S3_MAX_POOL_CONNECTIONS', '20')),
        connect_timeout=int(os.getenv('AWS_S3_CONNECT_TIMEOUT', '10')),   # Connection timeout in seconds
        read_timeout=int(os.getenv('AWS_S3_READ_TIMEOUT', '5')),     # Read timeout in seconds
        retries={
            'max_attempts': 2,  # Retry attempts for failed requests
            'mode': 'standard'  # Retry mode can be 'standard' or 'adaptive'
        }
    )

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "PxGs5b1Rv4oA7Ig0xGoY")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "VnwammFFZlllBwIpoFBMNZt19tlbGMjoQz7U3Tem")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", 'accident-detect')
AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL", "http://localhost:9000/")
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = True
AWS_S3_FILE_OVERWRITE = False
