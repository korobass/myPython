#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Classes for Route53 domains."""

import uuid


class DomainManager:
    """Manage a Route 53 domain."""

    def __init__(self, session):
        """Create a DomainManager object."""
        self.session = session
        self.route53_client = self.session.client('route53')

    def find_hosted_zone(self, domain_name):
        """Find hosted zone by domain name."""
        paginator = self.route53_client.get_paginator('list_hosted_zones')
        for page in paginator.paginate():
            for zone in page['HostedZones']:
                if domain_name.endswith(zone['Name'][:-1]):
                    return zone

        return None

    def create_hosted_zone(self, domain_name):
        """Create Route 53 hosted zone."""
        zone_name = '.'.join(domain_name.split('.')[-2:]) + '.'
        return self.route53_client.create_hosted_zone(
            Name=zone_name,
            CallerReference=str(uuid.uuid4()),
            HostedZoneConfig={
                'Comment': 'Temporary hosted zone',
                'PrivateZone': False
            }
        )

    def create_s3_record(self, zone, domain_name, endpoint):
        """Create Alias record for the bucket."""
        return self.route53_client.change_resource_record_sets(
            HostedZoneId=zone['Id'],
            ChangeBatch={
                'Comment': 'Created by webotron',
                'Changes': [{
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': domain_name,
                        'Type': 'A',
                        'AliasTarget': {
                            'HostedZoneId': endpoint.zone,
                            'DNSName': endpoint.host,
                            'EvaluateTargetHealth': False
                        }
                    }
                }
                ]
            }
        )

    def create_cf_domain_record(self, zone, domain_name, cf_domain_name):
        """Create cloudfront record."""
        return self.route53_client.change_resource_record_sets(
            HostedZoneId=zone['Id'],
            ChangeBatch={
                'Comment': 'Created by webotron',
                'Changes': [{
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': domain_name,
                        'Type': 'A',
                        'AliasTarget': {
                            # according to aws docs
                            # https://docs.aws.amazon.com/Route53/latest/APIReference/API_AliasTarget.html
                            'HostedZoneId': 'Z2FDTNDATAQYW2',
                            'DNSName': cf_domain_name,
                            'EvaluateTargetHealth': False
                        }
                    }
                }
                ]
            }
        )

    def delete_cf_domain_record(self, zone, domain_name, cf_domain_name):
        """Delete CloudFront route53 record."""
        return self.route53_client.change_resource_record_sets(
            HostedZoneId=zone['Id'],
            ChangeBatch={
                'Changes': [{
                    'Action': 'DELETE',
                    'ResourceRecordSet': {
                        'Name': domain_name,
                        'Type': 'A',
                        'AliasTarget': {
                            # according to aws docs
                            # https://docs.aws.amazon.com/Route53/latest/APIReference/API_AliasTarget.html
                            'HostedZoneId': 'Z2FDTNDATAQYW2',
                            'DNSName': cf_domain_name,
                            'EvaluateTargetHealth': False
                        }
                    }
                }
                ]
            }
        )
