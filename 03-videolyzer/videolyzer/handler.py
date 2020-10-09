import urllib
import boto3
from pathlib import Path

def start_label_detection(bucket, key):
    """Start rekognition for a given s3 key."""
    rkg_client = boto3.client('rekognition')
    response = rkg_client.start_label_detection(
        Video={
            'S3Object': {
                'Bucket': bucket,
                'Name': key
            }
        })
    print(response)
    return

def start_processing_video(event, context):
    """Rekognition of mp4 video on upload do s3."""
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(
            record['s3']['object']['key']
        )
        start_label_detection(bucket, key)
