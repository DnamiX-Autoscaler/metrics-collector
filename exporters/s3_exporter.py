# exporters/s3_exporter.py

from typing import Optional
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from utils.logger import get_logger

logger = get_logger(__name__)


def upload_file_to_s3(
    file_path: str,
    bucket_name: str,
    object_key: str,
    aws_region: Optional[str] = None,
) -> bool:
    """
    Upload local file to S3.

    Requires AWS credentials to be configured in environment / ~/.aws/credentials.

    Returns:
      True if success, False if failure.
    """

    try:
        session = boto3.session.Session(region_name=aws_region) if aws_region else boto3
        s3 = session.client("s3") if aws_region else boto3.client("s3")

        s3.upload_file(file_path, bucket_name, object_key)
        logger.info("Uploaded %s to s3://%s/%s", file_path, bucket_name, object_key)
        return True

    except (BotoCoreError, ClientError) as e:
        logger.error("Failed to upload to S3: %s", e)
        return False
