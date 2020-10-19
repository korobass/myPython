# coding: utf-8
import boto3
from pathlib import Path


session = boto3.Session(profile_name='poc')
s3 = session.resource('s3')
bucket = s3.create_bucket(Bucket='poc-videolyzer', CreateBucketConfiguration={'LocationConstraint': session.region_name})
pathname = '~/Downloads/production ID_3929647.mp4'
path = Path(pathname).expanduser().resolve()
path
path.name
bucket.upload_file(str(path), str(path.name))
rk_client = session.client('rekognition')
response = rk_client.start_label_detection(Video={
    'S3Object': {
        'Bucket': bucket.name,
        'Name': path.name}
        }
    )

response
job_id = response['JobId']
result = rk_client.get_label_detection(JobId=job_id)

result.keys()
result['JobStatus']
result['ResponseMetadata']
result['Labels']
len(result['Labels'])

