import os
import json
import boto3
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure
from secretManager import getSecret
from globalBundle import getGlobalbundle

# Configura el cliente de S3 y DocumentDB
s3_client = boto3.client('s3')
documentdb = boto3.client('docdb')

# Nombre de la base de datos y colección en DocumentDB
db_name = os.environ['nameDatabase']
collection_name = os.environ['collectionDatabase']
secret = json.loads(getSecret(region=os.environ['AWS_REGION'], secret_manager_arn=os.environ['secretManagerArn']))

# Se obtiene el archivo temporal
getGlobalbundle()

def lambda_handler(event, context):
    
    print(json.dumps(event))

    print(json.dumps(event["body"]))

    json_data = json.loads(event["body"])

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
        print(json.dumps(f'Guadado en el id: {db_result.inserted_id}'))
        return {
            'statusCode': 200,
            'body': json.dumps(f'Guadado en el id: {db_result.inserted_id}')
        }
        
    except (ConnectionError, ServerSelectionTimeoutError, OperationFailure) as e:
        error_message = "Error: No se pudo conectar con la base de datos."
        print(error_message)
        return {
            'statusCode': 500,
            'body': json.dumps(error_message)
        }

    except Exception as e:
        print("Error al insertar en DocumentDB:", e)
        return {
            'statusCode': 500,
            'body': json.dumps("Error interno al insertar en la base de datos")
        }
