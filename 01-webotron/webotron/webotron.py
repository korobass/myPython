#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Webotron: Deploy websites with aws.

Webotron automates the process of deploying static websites to AWS
- Configure AWS S3 buckets
    - Create tehm
    - Set them up for static website hosting
    - Deploy local files to them
- Configure DNS record with AWS Route 53
- Configure a Content Delivery Network and SSL with AWS CloudFront
"""

import sys
import boto3
import click
from bucket import BucketManager


SESSION = None
BUCKET_MANAGER = None


@click.group()
@click.option('--profile', default=None,
              help="Use a given AWS profile.")
@click.option('--region', default=None,
              help="Use a given AWS region.")
def cli(profile, region):
    """Webotron deploys websites to AWS."""
    global SESSION, BUCKET_MANAGER
    session_cfg = {}
    if profile:
        session_cfg['profile_name'] = profile
    else:
        sys.exit("Be careful when using default aws profile. \
                 Use --profile=name instead")
    if region:
        session_cfg['region_name'] = region

    SESSION = boto3.Session(**session_cfg)
    BUCKET_MANAGER = BucketManager(SESSION)


@cli.command('list-buckets')
def list_buckets():
    """List all s3 buckets."""
    for bucket in BUCKET_MANAGER.all_buckets():
        print(bucket)


@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    """List objects in s3 bucket."""
    for obj in BUCKET_MANAGER.all_objects(bucket):
        print(obj)


@cli.command('setup-bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    """Create and configure static website on s3."""
    s3_bucket = BUCKET_MANAGER.init_bucket(bucket)
    BUCKET_MANAGER.set_policy(s3_bucket)
    BUCKET_MANAGER.configure_website(s3_bucket)


@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket')
def sync(pathname, bucket):
    """Sync content of local directory to bucket."""
    BUCKET_MANAGER.sync(pathname, bucket)
    print(BUCKET_MANAGER.get_bucket_url(BUCKET_MANAGER.s3.Bucket(bucket)))


if __name__ == '__main__':
    cli()
