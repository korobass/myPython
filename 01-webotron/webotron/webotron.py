#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Webotron: Deploy websites with aws.

Webotron automates the process of deploying static websites to AWS
- Configure AWS S3 buckets
    - Create tehm
    - Set them up for static website hosting
    - Deploy local files to them
- Configure DNS recored with AWS Route 53
- Configure a Content Delivery Network and SSL with AWS CloudFront
"""

from pathlib import Path
import mimetypes
import boto3
from botocore.exceptions import ClientError
import click

session = boto3.Session(profile_name='ipfdigital-poc')
s3 = session.resource('s3')


@click.group()
def cli():
    """Webotron deploys websites to AWS."""
    pass


@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    """List objects in s3 bucket."""
    for obj in s3.Bucket(bucket).objects.all():
        print(obj)


@cli.command('list-buckets')
def list_buckets():
    """List all s3 buckets."""
    for bucket in s3.buckets.all():
        print(bucket)


@cli.command('setup-bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    """Create and configure static website on s3."""
    """ initiating variable before try/except """
    s3_bucket = None
    try:
        s3_bucket = s3.create_bucket(
            Bucket=bucket,
            CreateBucketConfiguration={
                'LocationConstraint': session.region_name
            }
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            s3_bucket = s3.Bucket(bucket)
        else:
            raise e

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
    """ % s3_bucket.name
    policy = policy.strip()
    pol = s3_bucket.Policy()
    pol.put(Policy=policy)
    ws = s3_bucket.Website()
    ws.put(WebsiteConfiguration={
            'ErrorDocument': {'Key': 'index.html'},
            'IndexDocument': {'Suffix': 'index.html'}
        }
    )
    return


def upload_file(s3_bucket, path, key):
    """Upload file to s3 bucket."""
    content_type = mimetypes.guess_type(key)[0] or 'text/plain'
    s3_bucket.upload_file(
        path,
        key,
        ExtraArgs={
            'ContentType': 'text/html'
        }
    )


@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket')
def sync(pathname, bucket):
    """Sync content of local directory to bucket."""
    s3_bucket = s3.Bucket(bucket)

    root = Path(pathname).expanduser().resolve()

    def handle_directory(target):
        """Go recursively via directory and upload all files."""
        for p in target.iterdir():
            if p.is_dir():
                handle_directory(p)
            if p.is_file():
                upload_file(s3_bucket, str(p), str(p.relative_to(root)))

    handle_directory(root)


if __name__ == '__main__':
    cli()
