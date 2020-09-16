#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Classes for ACM certificate."""

import time


class CertificateManager:
    """Manage a ACM certificates."""

    def __init__(self, session):
        """Create a CertManager object."""
        self.session = session
        self.acm_client = self.session.client('acm', region_name='us-east-1')

    def cert_matches(self, cert_arn, domain_name):
        """Find certificate usint alternative subject."""
        cert_details = self.acm_client.describe_certificate(
            CertificateArn=cert_arn
        )
        alt_names = cert_details['Certificate']['SubjectAlternativeNames']
        for name in alt_names:
            if name == domain_name:
                return True
            # wildcard domain
            if name[:2] == '*.' and \
                    domain_name.endswith(name[2:]) and \
                    domain_name.count('.') == name.count('.'):
                return True

        return False

    def find_cert(self, domain_name):
        """Find hosted zone by domain name."""
        paginator = self.acm_client.get_paginator('list_certificates')
        for page in paginator.paginate(CertificateStatuses=['ISSUED']):
            for cert in page['CertificateSummaryList']:
                if self.cert_matches(cert['CertificateArn'], domain_name):
                    return cert
        return None

    def create_cert(self, domain_name):
        """Create acm cert."""
        cert = self.acm_client.request_certificate(
            DomainName=domain_name,
            ValidationMethod='DNS',
            SubjectAlternativeNames=[
                domain_name
            ],
            Tags=[{
                    'Key': 'Name',
                    'Value': domain_name
                }]
        )
        # wait before getting info about a cert
        # to give time for AWS API for r53
        time.sleep(10)
        cert_details = self.acm_client.describe_certificate(
            CertificateArn=cert['CertificateArn']
        )

        return cert_details

    def await_acm_validation(self, cert_arn):
        """Check if certificate is valid."""
        waiter = self.acm_client.get_waiter('certificate_validated')
        waiter.wait(
            CertificateArn=cert_arn,
            WaiterConfig={
                'Delay': 10,
                'MaxAttempts': 20
            }
        )
