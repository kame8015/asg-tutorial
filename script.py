#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import io
from PIL import Image, ImageOps
import time
import os

BUCKET_NAME = os.getenv("BUCKET_NAME", None)
INPUT_PATH = "input/"

if BUCKET_NAME is None:
    raise Exception("BUCKET_NAME is not defined!")


class S3Client:
    def __init__(self):
        print("creating s3 client...")
        self.s3 = boto3.client("s3", region_name="ap-northeast-1")
        # s3 = boto3.resource("s3")
        # bucket_name = os.getenv("BUCKET_NAME")
        # self.bucket = s3.Bucket(bucket_name)
        # print(f"bucket name: {self.bucket.name}")

    def list_buckets(self):
        bucket_list = self.s3.list_buckets()["Buckets"]
        bucket_names = []
        for bucket in bucket_list:
            bucket_names.append(bucket["Name"])
        return bucket_names

    # def get_object(self, file_name):
    #     obj = self.bucket

    def list_objects(self, bucket_name, prefix):
        response = self.s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        objects = []
        for object in response["Contents"]:
            objects.append(object["Key"])
        return objects


if __name__ == "__main__":
    print("Invoked!!!!!!")
    # bucket_names = S3Client().list_buckets()

    # print(bucket_names)
    objects = S3Client().list_objects(bucket_name=BUCKET_NAME, prefix=INPUT_PATH)
    print(objects)