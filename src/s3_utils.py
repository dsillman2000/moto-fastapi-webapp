from functools import lru_cache
import moto
import boto3
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mypy_boto3_s3.client import S3Client
    from mypy_boto3_s3.type_defs import (
        ListBucketsOutputTypeDef,
        ObjectTypeDef,
        ListObjectsV2OutputTypeDef,
    )
    from mypy_boto3_s3.service_resource import Bucket, Object

from pathlib import Path
import re

MOCK_S3_PATH = Path(__file__).parent.parent / ".mock.s3"
MOCK_GRP_PATTERN = re.compile(r"```s3:\/\/([A-Za-z0-9\-]+)\/(.+?)\n((?:.|\n)+?)\n```")


def populate_mock_s3(s3_client: "S3Client"):
    mock_groups = MOCK_GRP_PATTERN.findall(MOCK_S3_PATH.read_text())

    distinct_buckets = set(bucket for bucket, _, _ in mock_groups)
    for bucket in distinct_buckets:
        s3_client.create_bucket(Bucket=bucket)

    for bucket, key, body in mock_groups:
        s3_client.put_object(Bucket=bucket, Key=key, Body=body)


TEST_ENV_VAR = True  # os.getenv("TEST", False)


@lru_cache
def get_or_create_s3() -> "S3Client":
    if TEST_ENV_VAR:
        print("Mocking AWS with moto " + moto.__version__)
        mock = moto.mock_aws()
        mock.start()

    s3: "S3Client" = boto3.client("s3")

    if TEST_ENV_VAR:
        populate_mock_s3(s3)
    return s3


class S3Context:
    __s3_client: "S3Client"

    def __init__(self):
        self.__s3_client = get_or_create_s3()

    @property
    def buckets(self):
        list_buckets: "ListBucketsOutputTypeDef" = self.__s3_client.list_buckets()
        return [
            {"name": bucket["Name"], "creation_date": bucket["CreationDate"]}
            for bucket in list_buckets["Buckets"]
        ]

    def bucket(self, bucket_name: str) -> "Bucket":
        b: "Bucket" = boto3.resource("s3").Bucket(bucket_name)
        return b

    def get_objects_in(self, bucket_name: str, prefix: str) -> "list[ObjectTypeDef]":
        list_objects: "ListObjectsV2OutputTypeDef" = self.__s3_client.list_objects_v2(
            Bucket=bucket_name, Prefix=prefix, Delimiter="/"
        )
        objs: list["ObjectTypeDef"] = list_objects.get("Contents", [])
        return objs

    def get_dirs_in(self, bucket_name: str, prefix: str) -> "list[str]":
        list_objects: "ListObjectsV2OutputTypeDef" = self.__s3_client.list_objects_v2(
            Bucket=bucket_name, Prefix=prefix, Delimiter="/"
        )
        return [cp["Prefix"] for cp in list_objects.get("CommonPrefixes", [])]

    def dict(self):
        return {"s3": self}
