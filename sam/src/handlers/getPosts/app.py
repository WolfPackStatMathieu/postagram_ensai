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

def get_posts(user=None):
    """ Cette méthode récupére les publications depuis la base de données. 
        Elle prend un paramètre facultatif user pour filtrer les publications pour un utilisateur spécifique. 
        Si user est fourni, la fonction effectue une requête basée sur cet utilisateur ; sinon, elle parcourt 
        l'ensemble de la table pour récupérer toutes les publications.
    """
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.getenv("POSTS_TABLE"))
    logger.info(str(user))
    if user:
    
        response = table.query(
            KeyConditionExpression=Key('user').eq(user) 
        )
    else:
        response = table.scan()

    posts = response['Items']
    logger.info(str(posts))
    return posts

def generate_signed_url(object_name):
    """ Cette méthode est utilisée pour générer une URL signée pour un objet S3 en fonction de son nom. 
    """
    try:
        url = s3_client.generate_presigned_url(
            Params={
                "Bucket": bucket,
                "Key": object_name
            },
            ClientMethod='get_object'
        )
        return url
    except ClientError as e:
        logger.error(e)
        return None

def lambda_handler(event, context):
    """
    Ce code met à jour, récupère les publications depuis la base de données, génère des URL signées pour 
    les images et renvoie les publications traitées dans le format attendu.
    """

    
    # Selon la présence du paramètre user, la fonction 
    # get_posts est appelée avec les arguments appropriés.
    
    if event.get("queryStringParameters") and event["queryStringParameters"].get("user"):
        requested_user = event["queryStringParameters"]["user"]
        posts = get_posts(user=requested_user)
    else:
        posts = get_posts()


    response = {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': '*'
        },
        "body": json.dumps(posts)
    }

    return response


