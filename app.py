from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, messaging
import os
import json

# Inicializa la aplicación Flask
app = Flask(__name__)

# Cargar credenciales de Firebase desde una variable de entorno
def initialize_firebase():
    # Obtén la cadena JSON de la variable de entorno
    firebase_credentials = os.getenv('FIREBASE_CREDENTIALS')

    # Verifica si la variable de entorno está configurada
    if not firebase_credentials:
        raise ValueError("La variable de entorno FIREBASE_CREDENTIALS no está configurada.")

    # Convierte la cadena JSON en un diccionario
    try:
        cred_dict = json.loads(firebase_credentials)
    except json.JSONDecodeError as e:
        raise ValueError(f"La variable de entorno FIREBASE_CREDENTIALS no contiene un JSON válido: {str(e)}")

    # Inicializa Firebase Admin SDK
    try:
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        print("Firebase inicializado correctamente.")
    except Exception as e:
        raise ValueError(f"Error al inicializar Firebase: {str(e)}")

# Ruta para enviar notificaciones
@app.route('/send-notification', methods=['POST'])
def send_notification():
    data = request.get_json()
    token = data.get('token')
    title = data.get('title', 'Notificación')
    body = data.get('body', 'Mensaje de Firebase')

    if not token:
        return jsonify({"success": False, "error": "Token de dispositivo no proporcionado"}), 400

    # Construir el mensaje
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=token
    )

    try:
        # Enviar la notificación
        response = messaging.send(message)
        print(f"Notificación enviada correctamente. Message ID: {response}")
        return jsonify({"success": True, "message_id": response})
    except Exception as e:
        print(f"Error al enviar la notificación: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# Inicializa Firebase al iniciar la aplicación
try:
    initialize_firebase()
except Exception as e:
    print(f"Error crítico al inicializar Firebase: {str(e)}")
    exit(1)

# Iniciar la aplicación Flask
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Usa el puerto de Render o 10000 por defecto
    app.run(host='0.0.0.0', port=port)
