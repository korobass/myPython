#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Classes for S3 Buckets."""
import boto3
import mimetypes
from pathlib import Path
import re
import sys
from botocore.exceptions import ClientError
from hashlib import md5
from functools import reduce


class BucketManager:
    """Manage an S3 Bucket."""
    CHUNK_SIZE = 8388608
    def __init__(self, session):
        """Create a BucketManager object."""
        self.session = session
        self.s3 = self.session.resource('s3')
        self.transfer_config = boto3.s3.transfer.TransferConfig(
            multipart_threshold=self.CHUNK_SIZE,
            multipart_chunksize=self.CHUNK_SIZE
        )
        self.manifest = {}

    def all_buckets(self):
        """Get an iterator for all buckets."""
        return self.s3.buckets.all()

    def get_bucket_region_name(self, bucket_name):
        """Get the bucket's region name."""
        client = self.s3.meta.client
        bucket_location = client.get_bucket_location(Bucket=bucket_name)
        return bucket_location["LocationConstraint"]

    def get_bucket_url(self, bucket):
        """
        Get static website URL.

        https://docs.aws.amazon.com/AmazonS3/latest/dev/WebsiteEndpoints.html
        http://bucket-name.s3-website.Region.amazonaws.com/folder-name/object-name
        """
        return 'http://' + bucket.name + \
               '.s3-website.' + self.get_bucket_region_name(bucket.name) + \
               '.amazonaws.com'

    def all_objects(self, bucket_name):
        """Get all objects of a bucket."""
        if not self.is_valid_bucket_name(bucket_name):
            sys.exit(self.print_aws_s3_doc())

        return self.s3.Bucket(bucket_name).objects.all()

    def init_bucket(self, bucket_name):
        """Create a new bucket, or return existing one by name."""
        if not self.is_valid_bucket_name(bucket_name):
            sys.exit(self.print_aws_s3_doc())
        s3_bucket = None
        try:
            s3_bucket = self.s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': self.session.region_name
                }
            )
        except ClientError as error:
            if error.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                s3_bucket = self.s3.Bucket(bucket_name)
            else:
                raise error

        return s3_bucket

    @staticmethod
    def set_policy(bucket):
        """Set bucket policy to be public readable."""
        policy = """
        {
          "Version":"2012-10-17",
          "Statement":[
            {
              "Sid":"PublicReadGetObject",
              "Effect":"Allow",
              "Principal": "*",
              "Action":["s3:GetObject"],
              "Resource":["arn:aws:s3:::%s/*"]
              }
          ]
        }
        """ % bucket.name
        policy = policy.strip()
        pol = bucket.Policy()
        pol.put(Policy=policy)

    @staticmethod
    def configure_website(bucket):
        """Configure static website on S3."""
        website = bucket.Website()
        website.put(WebsiteConfiguration={
            'ErrorDocument': {'Key': 'index.html'},
            'IndexDocument': {'Suffix': 'index.html'}
            }
        )

    def load_manifest(self, bucket_name):
        """Load manifest for caching purposes.
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Paginator.ListObjectsV2
        """

        paginator = self.s3.meta.client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket_name):
            for obj in page.get('Contents', []):
                self.manifest[obj['Key']] = obj['ETag']
                #pprint(obj)

    @staticmethod
    def hash_data(data):
        """Generate md5 hash of data."""
        hash = md5()
        hash.update(data)

        return hash

    def gen_etag(self, filepath):
        """Generate ETag based on local file"""
        hashes = []

        with open(filepath, 'rb') as file:
            while True:
                # Read only the data of file up to the size
                data = file.read(self.CHUNK_SIZE)
                if not data:
                    break
                hashes.append(self.hash_data(data))
        # if empty file
        if not hashes:
            return
        # single file
        elif len(hashes) == 1:
            return '"{}"'.format(hashes[0].hexdigest())
        else:
            # algorithm that AWS is using to generate ETAG for large files
            hash = self.hash_data(
                reduce(
                    lambda x, y: x+y,
                    (h.digest() for h in hashes)
                )
            )
            return '"{}-{}"'.format(hash.hexdigest(), len(hashes))


        # format exactly as in s3 objects metadata:
        # e. g. 'ETag': '"56f7206f131f959afec172068057ac16"'



    def upload_file(self, bucket, path, key):
        """Upload file to s3 bucket."""
        content_type = mimetypes.guess_type(key)[0] or 'text/plain'
        etag = self.gen_etag(path)
        if self.manifest.get(key, '') == etag:
            print("Skipping {}, etag.match".format(key))
            return

        print("Uploading {}, new file".format(key))
        return bucket.upload_file(
            path,
            key,
            ExtraArgs={
                'ContentType': content_type
            },
            Config=self.transfer_config
        )

    @staticmethod
    def print_aws_s3_doc():
        """Print AWS Bucket naming requirements doc."""
        return print('Invalid bucket name, please refer to documentation: \
        https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-s3-bucket-naming-requirements.html')

    @staticmethod
    def is_valid_bucket_name(bucket_name):
        """Verify if bucket follow aws naming requirements."""
        if not 3 < len(bucket_name) < 63:
            return False
        bucket_name_regex = re.compile(
            r'^[a-z0-9]([a-z-0-9-]{0,61}[a-z0-9])?$',
            re.VERBOSE
        )
        return bucket_name_regex.match(bucket_name)

    def sync(self, pathname, bucket_name):
        """Sync local folder to s3 bucket."""

        # verify if bucket has a valid name
        if not self.is_valid_bucket_name(bucket_name):
            sys.exit(self.print_aws_s3_doc())

        bucket = self.s3.Bucket(bucket_name)
        self.load_manifest(bucket_name)

        root = Path(pathname).expanduser().resolve()

        def handle_directory(target):
            """Go recursively via directory and upload all files."""
            for path in target.iterdir():
                if path.is_dir():
                    handle_directory(path)
                if path.is_file():
                    self.upload_file(bucket, str(path), str(path.relative_to(root)))

        handle_directory(root)
