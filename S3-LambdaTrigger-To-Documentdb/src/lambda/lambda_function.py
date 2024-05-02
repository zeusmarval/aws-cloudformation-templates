import os
import json
import boto3
from pymongo import MongoClient
from secretManager import getSecret
from globalBundle import getGlobalbundle

# Configura el cliente de S3 y DocumentDB
s3_client = boto3.client('s3')
documentdb = boto3.client('docdb')

# Nombre de la base de datos y colección en DocumentDB
db_name = os.environ['nameDatabase']
collection_name = os.environ['collectionDatabase']
secret = json.loads(getSecret(region= os.environ['region'], secret_manager_arn=os.environ['secretManagerArn']))

# Se obtiene el archivo temporal
getGlobalbundle()

def lambda_handler(event, context):

    # Evento que activa la lambda
    print(json.dumps(event))

    # Obtencion de credenciales para documentdb
    for record in event['Records']:
        # Obtiene información sobre el archivo desde el evento
        bucket_name = record['s3']['bucket']['name']
        file_key = record['s3']['object']['key']
        
        # Descarga el archivo JSON desde S3
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        json_data = json.loads(response['Body'].read().decode('utf-8'))

        # Inserta el JSON en la colección de DocumentDB
        return insert_into_documentdb(json_data)

def insert_into_documentdb(json_data):
    # Convierte el JSON en un formato que DocumentDB puede entender
    document = json.loads(json.dumps(json_data))

    # Conecta con DocumentDB
    cluster_endpoint = f"{secret['username']}:{secret['password']}@{secret['host']}"
    port = secret['port']
    connection_string = f"mongodb://{cluster_endpoint}:{port}/{os.environ['databasePreference']}"
    
    # Inserta el documento en DocumentDB
    try:
        client = MongoClient(connection_string)
        db = client[db_name]
        collection = db[collection_name]
        db_result = collection.insert_one(document)
        return {
            'statusCode': 200,
            'body': json.dumps(f'Guadado en el id: {db_result.inserted_id}')
        }

    except Exception as e:
        print("Error al insertar en DocumentDB:", e)
        return e
