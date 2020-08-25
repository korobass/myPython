# coding: utf-8
import boto3
session = boto3.Session(profile_name='ipfdigital-poc')
s3 = session.resource('s3')    
ec2_client = session.client('ec2')
