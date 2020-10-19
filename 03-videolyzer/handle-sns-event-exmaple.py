# coding: utf-8
cos={'Records': [{'EventSource': 'aws:sns', 'EventVersion': '1.0', 'EventSubscriptionArn': 'arn:aws:sns:eu-west-1:910005352337:handleLabelDetectionTopic:3a6cf44d-b72c-4819-af4b-7e95a74b3527', 'Sns': {'Type': 'Notification', 'MessageId': '2ba65674-2357-541a-8fbb-0e73ad0c311a', 'TopicArn': 'arn:aws:sns:eu-west-1:910005352337:handleLabelDetectionTopic', 'Subject': None, 'Message': '{"JobId":"20af08d209f389a0b473a4d22f08d8239ea18800be1ce797f0e19dd90b09bb5d","Status":"SUCCEEDED","API":"StartLabelDetection","Timestamp":1603111963683,"Video":{"S3ObjectName":"production ID_3929647.mp4","S3Bucket":"poc-videolyzer"}}', 'Timestamp': '2020-10-19T12:52:43.759Z', 'SignatureVersion': '1', 'Signature': 'enfyOVhNUj0nAxgryNjyvNstUDTYFtrCmq7Y5433L9LoKc+/UGjW/pwYTqAv8lDJyBcYyhpS28tE6rgqverTlpdr7WL6GG8Z3FmGQ1F9Jp6DoiHyxt/hPq1D3mSOWLB8nbbOVstbnzSkxpC9PdBM3HwaENJogoIGjFdbGtP+9zPj3xJtWF5Mn5MtQkzXopIk1xNyA5nAQ1qisnTPKCrGzb92pr8NgmrCACR7p9lxESlJmHYVbgbwQzvE1PDLHTth8fg9B6mJ8Ljcth9mh8LnAaU2iw/jtIclLCpBl/HAeTXc7IrC+Q9oeQzhPMtRIX8KW3CTNX9H9pH6h/HnF44QAg==', 'SigningCertUrl': 'https://sns.eu-west-1.amazonaws.com/SimpleNotificationService-a86cb10b4e1f29c941702d737128f7b6.pem', 'UnsubscribeUrl': 'https://sns.eu-west-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:eu-west-1:910005352337:handleLabelDetectionTopic:3a6cf44d-b72c-4819-af4b-7e95a74b3527', 'MessageAttributes': {}}}]}
cos
cos.keys
cos.keys()
cos['Records'][0]
cos['Records'][0].keys()
cos['Records'][0].['EventSource']
cos['Records'][0]['EventSource']
cos['Records'][0]['EventVersion']
cos['Records'][0]['EventSubscriptoinArn']
cos['Records'][0]['EventSubscriptionArn']
cos['Records'][0]['Sns']
cos['Records'][0]['Sns']['Message']
cos['Records'][0]['Sns']['Message']['JobId']
import json
json.loads(cos['Records'][0]['Sns']['Message'])
