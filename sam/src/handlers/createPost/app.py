# import requests

import json
import uuid
import boto3
import os



def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """


    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.getenv("POSTS_TABLE"))
    
    body = json.loads(event['body'])
    # get username
    user = event["headers"]["Authorization"]

    
    # object to be inserted
    data = table.put_item(
            Item = { 
                    'id': str(uuid.uuid4()),
                    'user': body['user'],
                    'title': body['title'],
                    'body': body['body'],
                    }
                )

    response = {
                "statusCode": 200,
                "headers": {
                'Access-Control-Allow-Origin': '*'
            },
            "body":json.dumps(data)
        }
    
    return response

