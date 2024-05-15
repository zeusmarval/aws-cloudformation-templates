import os
import json
from jose import jwt, JWTError
from secretManager import getSecret
from datetime import datetime, timezone

# Obtener el secreto que contiene la clave secreta para validar el JWT
secret_key = json.loads(getSecret(region=os.environ['AWS_REGION'], secret_manager_arn=os.environ['secretManagerArn']))

def lambda_handler(event, context):
    print(json.dumps(event))
    
    principal_id = '0001'
    
    try:
        # Extraer el JWT del evento de la solicitud
        token = event['authorizationToken']

        # Validar el JWT utilizando la clave secreta
        payload = jwt.decode(token, secret_key['secretkey'], algorithms=['HS256'])
        
        # Data
        print(payload)

        # Si la validación es exitosa, se permite la autorización
        principal_id = payload['sub']
        effect = 'Allow'
    except JWTError as e:
        print(f"Error al validar el JWT: {e}")
        effect = 'Deny'
        # Devolver una respuesta de error adecuada
        errorMessage = f"Error al validar el JWT: {e}"
    except Exception as e:
        print(f"Error: {e}")
        effect = 'Deny'
        # Devolver una respuesta de error adecuada
        errorMessage = f"Error: {e}"
            
    # Construir la política de autorización
    auth_response = {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': event['methodArn']
                }
            ]
        }
    }

    if effect == 'Deny':
        auth_response['context'] = {
            'errorMessage': errorMessage
        }
        return auth_response
    else:
        return auth_response
