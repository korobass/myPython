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
import util
from bucket import BucketManager
from cdn import DistributionManager
from domain import DomainManager
from acm import CertificateManager


SESSION = None
BUCKET_MANAGER = None
DOMAIN_MANAGER = None
CERTIFICATE_MANAGER = None
DIST_MANAGER = None


@click.group()
@click.option('-p', '--profile', default=None,
              help="Use a given AWS profile.")
@click.option('-r', '--region', default=None,
              help="Use a given AWS region.")
def cli(profile, region):
    """Webotron deploys websites to AWS."""
    global SESSION, BUCKET_MANAGER,\
        DOMAIN_MANAGER, CERTIFICATE_MANAGER, DIST_MANAGER
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
    DOMAIN_MANAGER = DomainManager(SESSION)
    CERTIFICATE_MANAGER = CertificateManager(SESSION)
    DIST_MANAGER = DistributionManager(SESSION)


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
@click.option('-d', '--delete', is_flag=True,
              help="Files that exist in the destination\
               but not in the source are deleted during sync.")
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket')
def sync(delete, pathname, bucket):
    """Sync content of local directory to bucket."""
    BUCKET_MANAGER.sync(pathname, bucket)
    if delete:
        BUCKET_MANAGER.delete_missing_objects(bucket)

    print("bucket url: " +
          BUCKET_MANAGER.get_bucket_url(BUCKET_MANAGER.s3_res.Bucket(bucket)))


@cli.command('delete-bucket')
@click.argument('bucket')
def delete_bucket(bucket):
    """Delete bucket."""
    BUCKET_MANAGER.delete_bucket(bucket)


@cli.command('setup-domain')
@click.argument('domain')
def setup_domain(domain):
    """Add custom domain name for bucket website."""
    zone = DOMAIN_MANAGER.find_hosted_zone(domain) \
        or DOMAIN_MANAGER.create_hosted_zone(domain)

    bucket_region = BUCKET_MANAGER.get_bucket_region_name(domain)
    endpoint = util.get_endpoint(bucket_region)
    DOMAIN_MANAGER.create_s3_record(zone, domain, endpoint)
    print("Domain configured: http://{}".format(domain))


@cli.command('setup-cdn')
@click.argument('domain')
def setup_cdn(domain):
    """Add cloudfront for bucket website."""
    dist = DIST_MANAGER.find_matching_dist(domain)
    if not dist:
        cert = CERTIFICATE_MANAGER.find_cert(domain)
        cert_arn = cert['CertificateArn']
        if not cert:
            cert = CERTIFICATE_MANAGER.create_cert(domain)
            cert_arn = cert['Certificate']['CertificateArn']
            # handle exception here KeyError: 'Certificate'
            if cert['Certificate']['Status'] == 'PENDING_VALIDATION':
                DOMAIN_MANAGER.create_acm_cname_record(
                    domain,
                    cert['Certificate']['DomainValidationOptions']
                    [0]['ResourceRecord']
                )
        print("Waiting for ACM certificate DNS validation ...")
        CERTIFICATE_MANAGER.await_acm_validation(cert_arn)
        dist = DIST_MANAGER.create_dist(domain, cert_arn)

        print("Waiting for CloudFront distribution deployment ...")
        DIST_MANAGER.await_deploy(dist['Id'])

    zone = DOMAIN_MANAGER.find_hosted_zone(domain) \
        or DOMAIN_MANAGER.create_hosted_zone(domain)

    DOMAIN_MANAGER.create_cf_domain_record(zone, domain, dist['DomainName'])
    print("Domain configured: https://{}".format(domain))


@cli.command('delete-cdn')
@click.argument('domain')
def delete_cdn(domain):
    """Delete CloudFront distribution."""
    dist = DIST_MANAGER.find_matching_dist(domain)
    if dist:
        DIST_MANAGER.delete_dist(dist)
    else:
        print("There is no distribution named {}".format(domain))


if __name__ == '__main__':
    cli()
