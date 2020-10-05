# coding: utf-8
import boto3
session = boto3.Session(profile_name='poc')
as_client = session.client('autoscaling')
as_client.describe_auto_scaling_groups()
as_client.describe_policies()
as_client.execute_policy(AutoScalingGroupName='poc-eks-c20191218134355000900000002')
get_ipython().run_line_magic('save', 'autoscale_example.py 1-8')
