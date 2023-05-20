import boto3
import os
import logging
import json
from datetime import datetime
from urllib.parse import unquote_plus

table_name = os.getenv("POSTS_TABLE")
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)
reckognition = boto3.client('rekognition')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Pour logger
    logger.info(json.dumps(event, indent=2))
    # Récupération du nom du bucket
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    # Récupération du nom de l'objet
    logger.info(unquote_plus(event["Records"][0]["s3"]["object"]["key"]))
    key = unquote_plus(event["Records"][0]["s3"]["object"]["key"])
    # extration de l'utilisateur et de l'id de la tâche
    user, task_id = key.split('/')[:2]
    
    # Appel au service, en passant l'image à analyser (bucket et key)
    # On souhaite au maximum 5 labels et uniquement les labels avec 
    # un taux deconfiance > 0.75
    # Vous pouvez faire varier ces valeurs.
    label_data = reckognition.detect_labels(
    Image={
        "S3Object": {
        "Bucket": bucket,
        "Name": key
    }

    },
    MaxLabels=5,
    MinConfidence=0.75
    )

    logger.info(f"Labels data : {label_data}")
    # On extrait les labels du résultat
    labels = [label["Name"] for label in label_data["Labels"]]
    logger.info(f"Labels detected : {labels}")


    # Création de l'item à mettre à jour dans la base de données DynamoDB
    item = {
        'user': user,
        'id': task_id,
        'labels': labels,
        'image_location': f's3://{bucket}/{key}'
    }

    # Mise à jour de l'item dans la base de données DynamoDB
    data = table.update_item(
        Key={
            'user': user,
            'id': task_id
        },
        UpdateExpression='SET labels = :labels, image_location = :image_location',
        ExpressionAttributeValues={
            ':labels': labels,
            ':image_location': f's3://{bucket}/{key}' #adresse du bucket
        }
    )
    
    response = {
                "statusCode": 200,
                "headers": {
                'Access-Control-Allow-Origin': '*'
            },
            "body":json.dumps(data)
        }
    logger.info(f'body: {response["body"]}')

    return response