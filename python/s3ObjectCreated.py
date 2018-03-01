import boto3
import json
import urllib.parse
from botocore.exceptions import ClientError

s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    response = send_email(bucket, key)
    return response

def send_email(bucket, key):
    # Replace EMAIL with the email of the message sender/recipients - must be verified in SES
    sender = "NAME <EMAIL>"
    recipients = ["EMAIL"]
    aws_region = "us-east-1"
    subject = "S3 Object Created Notification"
    charset = "UTF-8"

    message_text = ("S3 Object Created\r\n"
                "Bucket: " + bucket + "\n"
                "Key: " + key)
                
    message_html = """<html>
    <head></head>
    <body>
    <h1>S3 Object Created</h1>
    <p>Bucket: """ + bucket + """<br>
    Key: """ + key + """</p>
    </body>
    </html>"""            

    try:
        client = boto3.client('ses', region_name=aws_region)
        response = client.send_email(
            Destination={
                'ToAddresses': recipients,
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': charset,
                        'Data': message_html,
                    },
                    'Text': {
                        'Charset': charset,
                        'Data': message_text,
                    },
                },
                'Subject': {
                    'Charset': charset,
                    'Data': subject,
                },
            },
            Source=sender,
        )
    except ClientError as e:
        return "Failed to send message: " + e.response['Error']['Message']
    else:
        status_code = response['ResponseMetadata']['HTTPStatusCode']
        if status_code == 200:
            return "Successfully sent message"
        else:
            return "Failed to send message: HTTP status code " + str(status_code)