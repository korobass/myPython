#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Classes for ACM certificate."""

from pprint import pprint


class CertificateManager:
    """Manage a ACM certificates."""

    def __init__(self, session):
        """Create a CertManager object."""
        self.session = session
        self.acm_client = self.session.client('acm')

    def cert_matches(self, cert_arn, domain_name):
        """Find certificate usint alternative subject"""
        cert_details = self.acm_client.describe_certificate(CertificateArn=cert_arn)
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