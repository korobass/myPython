import os
import urllib
import boto3
import json


def start_label_detection(bucket, key):
    """Start rekognition for a given s3 key."""
    rkg_client = boto3.client('rekognition')
    response = rkg_client.start_label_detection(
        Video={
            'S3Object': {
                'Bucket': bucket,
                'Name': key
            }
        },
        NotificationChannel={
            'SNSTopicArn': os.environ['REKOGNITION_SNS_TOPIC_ARN'],
            'RoleArn': os.environ['REKOGNITION_ROLE_ARN']
        })

    return

def get_video_labels(job_id):
    """Get rekognition labels based on job id."""
    rkg_client = boto3.client('rekognition')
    response = rkg_client.get_label_detection(JobId=job_id)
    next_token = response.get('NextToken', None)
    while next_token:
        next_page = rkg_client.get_label_detection(
            JobId=job_id,
            NextToken=next_token
        )
        next_token = response.get('NextToken', None)
        # extend is appending each item from the list
        response['Labels'].extend(next_page['Labels'])


    return response

def make_item(data):
    """Convert float to string."""
    if isinstance(data, dict):
        return { k: make_item(v) for k, v in data.items() }
    if isinstance(data, list):
        return [ make_item(v) for v in data ]
    if isinstance(data, float):
        return str(data)

    return data

def put_labels_in_db(data, video_name, video_bucket):
    """Write state into dynamodb table."""
    del data['ResponseMetadata']
    del data['JobStatus']

    data['videoName'] = video_name
    data['videoBucket'] = video_bucket
    data = make_item(data)
    dynamodb = boto3.resource('dynamodb')
    table_name = os.environ['DYNAMODB_TABLE_NAME']
    videos_table = dynamodb.Table(table_name)
    videos_table.put_item(Item=data)
    return

# Lambda events functions

def start_processing_video(event, context):
    """Rekognition of mp4 video on upload do s3."""
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(
            record['s3']['object']['key']
        )
        start_label_detection(bucket, key)


def handle_label_detection(event, context):
    """Print topic event."""
    for record in event['Records']:
        message = json.loads(record['Sns']['Message'])
        job_id = message['JobId']
        s3_object = message['Video']['S3ObjectName']
        s3_bucket = message['Video']['S3Bucket']

        response = get_video_labels(job_id)

        put_labels_in_db(response, s3_object, s3_bucket)

    return
