#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Classes for ACM certificate."""

import time
import uuid
from datetime import datetime, timedelta
import sys


class CDNManager:
    """Manage a ACM certificates."""

    def __init__(self, session):
        """Create a DistribiutionManager object."""
        self.session = session
        self.cf_client = self.session.client('cloudfront')

    def find_matching_dist(self, domain_name):
        """Find cloudfront distribution."""
        paginator = self.cf_client.get_paginator('list_distributions')
        for page in paginator.paginate():
            if 'Items' in page['DistributionList']:
                for dist in page['DistributionList']['Items']:
                    for alias in dist['Aliases']['Items']:
                        if alias == domain_name:
                            return dist

        return None

    def create_dist(self, domain_name, cert_arn):
        """Create cloudfront distribution."""
        # matching aws console behaviour
        origin_id = 'S3-' + domain_name
        # cloudfront config according to
        # https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/distribution-overview-required-fields.html
        result = self.cf_client.create_distribution(
            DistributionConfig={
                'CallerReference': str(uuid.uuid4()),
                'Aliases': {
                    'Quantity': 1,
                    'Items': [domain_name]
                },
                'DefaultRootObject': 'index.html',
                'Comment': 'Created by webotron',
                'Enabled': True,
                'Origins': {
                    'Quantity': 1,
                    'Items': [{
                        'Id': origin_id,
                        'DomainName':
                            '{}.s3.amazonaws.com'.format(domain_name),
                        'S3OriginConfig': {'OriginAccessIdentity': ''}
                    }]
                },
                'DefaultCacheBehavior': {
                    'TargetOriginId': origin_id,
                    'ViewerProtocolPolicy': 'redirect-to-https',
                    'TrustedSigners': {
                        'Quantity': 0,
                        'Enabled': False
                    },
                    'ForwardedValues': {
                        'Cookies': {'Forward': 'all'},
                        'Headers': {'Quantity': 0},
                        'QueryString': False,
                        'QueryStringCacheKeys': {'Quantity': 0}
                    },
                    'DefaultTTL': 86400,
                    'MinTTL': 3600
                },
                'ViewerCertificate': {
                    'ACMCertificateArn': cert_arn,
                    'SSLSupportMethod': 'sni-only',
                    'MinimumProtocolVersion': 'TLSv1.1_2016'
                }
            }
        )

        return result['Distribution']

    def await_deploy(self, dist_id):
        """Wait for dist to be deployed."""
        waiter = self.cf_client.get_waiter('distribution_deployed')
        waiter.wait(
            Id=dist_id,
            WaiterConfig={
                'Delay': 30,
                'MaxAttempts': 50
            }
        )

    def await_disabling(self, dist_id):
        """Wait for CF distribution disabling."""
        # https://stackoverflow.com/questions/43077173/deleting-a-cloudfront-distribution-with-boto3
        print("Waiting for disabling the distribution..."
              "This may take a while....")
        timeout_mins = 5
        wait_until = datetime.now() + \
            timedelta(minutes=timeout_mins)
        not_finished = True
        etag = None
        while not_finished:
            # check for timeout
            if wait_until < datetime.now():
                # timeout
                sys.exit("Distribution took too long to disable. Exiting")

            status = self.cf_client.get_distribution(
                Id=dist_id
            )
            enabled = status['Distribution']['DistributionConfig']['Enabled']
            deployed = status['Distribution']['Status']
            if enabled is False and deployed == 'Deployed':
                etag = status['ETag']
                not_finished = False

            print("Not completed yet. Sleeping 60 seconds....")
            time.sleep(60)

        return etag

    def delete_dist(self, dist):
        """Delete CloudFront distribution."""
        cf_config = self.cf_client.get_distribution_config(
            Id=dist['Id']
        )

        # Set distribution to disabled
        cf_config['DistributionConfig']['Enabled'] = False

        # you need to disable distribution first to be able to delete it
        self.cf_client.update_distribution(
            DistributionConfig=cf_config['DistributionConfig'],
            Id=dist['Id'],
            IfMatch=cf_config['ETag']
        )

        etag = self.await_disabling(dist['Id'])

        self.cf_client.delete_distribution(
            Id=dist['Id'],
            IfMatch=etag
        )
