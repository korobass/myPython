# coding: utf-8

import boto3

session = boto3.Session(profile_name='ipfdigital-poc')
ec2 = session.resource('ec2')