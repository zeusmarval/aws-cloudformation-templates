import os
import urllib.request

# Obtener archivo global-bundle de S3
def getGlobalbundle():
    
    try:
        url = os.environ['globalHundleUrl']
        filename = f"/tmp/{os.environ['globalHundleFile']}"
        urllib.request.urlretrieve(url, filename)
        print(f"Archivo descargado y guardado en {filename}")
    except Exception as e:
        print(f"Error al descargar el archivo: {str(e)}")