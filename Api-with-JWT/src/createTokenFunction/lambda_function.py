import os
import json
from jose import jwt
from datetime import datetime, timedelta
from secretManager import getSecret

# Obtener el secreto que contiene la clave secreta para validar el JWT
secret_key = json.loads(getSecret(region=os.environ['AWS_REGION'], secret_manager_arn=os.environ['secretManagerArn']))

def lambda_handler(event, context):

    print(json.dumps(event))
    
    data = json.loads(event['body'])

    # Validar que se proporcionen tanto el nombre de usuario como la contraseña
    if 'username' not in data or 'password' not in data:
        return {
            'statusCode': 400,
            'body': json.dumps('Se requiere tanto el nombre de usuario como la contraseña')
        }

    # Validar credenciales en SecretManager
    try:
        if data['username'] == secret_key['username'] and data['password'] == secret_key['password']:
            # Generar token JWT
            expiration_time = datetime.utcnow() + timedelta(days=int(os.environ['days']))
            unix_exp_time = int(expiration_time.timestamp())

            # Generar token JWT con expiración
            payload = {
                'sub': f'{int(datetime.utcnow().timestamp())}',
                'username': data['username'],
                'exp': unix_exp_time
            }
            # Datos generados
            print(payload)
            
            token = jwt.encode(payload, secret_key['secretkey'], algorithm='HS256')
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'token': token,
                    'expiration': expiration_time.strftime('%Y-%m-%dT%H:%M:%S')
                })
            }
        else:
            print('error: Credenciales inválidas')
            return {
                'statusCode': 401,
                'body': json.dumps('Credenciales inválidas')
            }
    except Exception as e:
        print(f'error {str(e)}')
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }
