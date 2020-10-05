# coding: utf-8
import boto3
session = boto3.Session(profile_name='poc')
as_client = session.client('autoscaling')

#as_client.execute_policy(AutoScalingGroupName='poc-eks-d20191230111420005100000002', PolicyName='Scale Up')
as_client.set_desired_capacity(
    AutoScalingGroupName='poc-eks-d20191230111420005100000002',
    DesiredCapacity=3,
)