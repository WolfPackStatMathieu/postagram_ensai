import json
import boto3
import os

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.getenv("POSTS_TABLE"))

    post_id = event["pathParameters"]["id"]  # Récupérer l'ID du post à supprimer

    # Supprimer la publication de la base de données
    table.delete_item(
        Key={
            'id': post_id
        }
    )

    # Supprimer l'image associée dans le bucket S3 (si applicable)

    response = {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': '*'
        },
        "body": json.dumps({"message": "Post deleted successfully"})
    }

    return response
