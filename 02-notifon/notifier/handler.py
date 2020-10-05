import os
import requests

def post_to_slack(event, context):
    """Post asg scale up event on the slack."""
    slack_webhook_url = os.environ['SLACK_WEBHOOK_URL']
    # using format to reference python dictionary
    slack_message = "From {source} at {detail[StartTime]}: {detail[Description]}".format(**event)
    emoji = ':smile:'
    data = { "username": post_to_slack.__name__,
            "text": slack_message,
             "icon_emoji": emoji}
    requests.post(slack_webhook_url, json=data)
    return

