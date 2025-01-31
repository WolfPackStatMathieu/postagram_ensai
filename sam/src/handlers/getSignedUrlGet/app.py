import logging
import boto3
from boto3.dynamodb.conditions import Key
import os
import json
import uuid
from pathlib import Path
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

bucket = os.getenv("S3_BUCKET")
s3_client = boto3.client('s3', config=boto3.session.Config(signature_version='s3v4'))

def lambda_handler(event, context):
    logger.info(event)
    user = event["requestContext"]["authorizer"]["claims"]["cognito:username"]

    if not event["queryStringParameters"].get("filename") :
        raise Exception('Parameter missing: filename')
           
    if not event["queryStringParameters"].get("filetype") :
        raise Exception('Parameter missing: filetype')
    
    if not event["queryStringParameters"].get("taskId") :
        raise Exception('Parameter missing: taskId')
    

    
    filename = f'{uuid.uuid4()}{Path(event["queryStringParameters"]["filename"]).name}'
    filetype = event["queryStringParameters"]["filetype"]
    task_id = event["queryStringParameters"]["taskId"]
    object_name = f"{user}/{task_id}/{filename}"

    try:
        url = s3_client.generate_presigned_url(
            Params={
            "Bucket": bucket,
            "Key": object_name,
            "ContentType": filetype
        },
            ClientMethod='get_object'
        )
    except ClientError as e:
        logging.error(e)


    logger.info(f'Url: {url}')

    response = {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': '*'
        },
        "body": json.dumps({
            "downloadURL": url,
            "objectName" : object_name
        })
    }

    logger.info('response: ' + json.dumps(response))
    return response