#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Classes for Route53 domains."""

import boto3
import uuid
from pprint import pprint
from webotron import util


class DomainManager:
    """Manage a Route 53 domain."""

    def __init__(self, session):
        """Create a DomainManager object."""
        self.session = session
        self.route53_client = self.session.client('route53')

    def find_hosted_zone(self, domain_name):
        """Find hosted zone by domain name"""
        paginator = self.route53_client.get_paginator('list_hosted_zones')
        for page in paginator.paginate():
            for zone in page['HostedZones']:
                if domain_name.endswith(zone['Name'][:-1]):
                    return zone

        return None

    def create_hosted_zone(self, domain_name):
        """Create Route 53 hosted zone"""
        zone_name = '.'.join(domain_name.split('.')[-2:]) + '.'
        return self.route53_client.create_hosted_zone(
            Name=zone_name,
            CallerReference=str(uuid.uuid4()),
            HostedZoneConfig={
                'Comment': 'Temporary hosted zone',
                'PrivateZone': False
            }
        )
    @staticmethod
    def get_s3_website_dns(bucket_name, region_name):
        """
        Get static website DNS.

        https://docs.aws.amazon.com/AmazonS3/latest/dev/WebsiteEndpoints.html
        http://bucket-name.s3-website.Region.amazonaws.com/folder-name/object-name
        """
        return bucket_name + \
               '.s3-website.' + region_name + \
               '.amazonaws.com'

    def create_s3_record(self, zone, domain_name,  bucket):
        """Create Alias record for the bucket"""
        region_name = bucket.get_region_name()
        endpoint = util.get_endpoint(region_name)
        s3_dns = self.get_s3_website_dns(bucket.name, region_name)
        return self.route53_client.change_resource_record_sets(
            HostedZoneId=zone['Id'],
            ChangeBatch={
                'Comment': bucket + 'website',
                'Changes': [
                    {
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': domain_name,
                            'Type': 'A',
                            'SetIdentifier': str(uuid.uuid4()),

                            'ResourceRecords': [
                                {
                                    'Value': 'string'
                                },
                            ],
                            'AliasTarget': {
                                'HostedZoneId': endpoint.zone,
                                'DNSName': s3_dns,
                                'EvaluateTargetHealth': False
                            }
                        }
                    }
                ]
            }
        )

