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
    except json.JSONDecodeError:
        raise ValueError("La variable de entorno FIREBASE_CREDENTIALS no contiene un JSON válido.")

    # Inicializa Firebase Admin SDK
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

# Ruta para enviar notificaciones
@app.route('/send-notification', methods=['POST'])
def send_notification():
    # Obtener los datos del cuerpo de la solicitud
    data = request.json
    user_token = data.get('user_token')  # Token FCM del dispositivo del usuario
    message_title = data.get('title')    # Título de la notificación
    message_body = data.get('body')      # Cuerpo de la notificación

    # Validar datos de entrada
    if not user_token or not message_title or not message_body:
        return jsonify({"success": False, "error": "Se requieren user_token, title y body"}), 400

    # Crear el mensaje de notificación
    notification = messaging.Notification(
        title=message_title,
        body=message_body
    )

    # Configurar el mensaje para FCM
    message = messaging.Message(
        notification=notification,
        token=user_token
    )

    try:
        # Enviar la notificación
        response = messaging.send(message)
        return jsonify({"success": True, "message_id": response})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Inicializa Firebase al iniciar la aplicación
initialize_firebase()

# Iniciar la aplicación Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
