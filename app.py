from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, messaging
import os
import json

# Inicializa la aplicación Flask
app = Flask(__name__)

# Función para inicializar Firebase
def initialize_firebase():
    firebase_credentials = os.getenv('FIREBASE_CREDENTIALS')
    if not firebase_credentials:
        raise ValueError("FIREBASE_CREDENTIALS no está configurada.")
    try:
        cred_dict = json.loads(firebase_credentials)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON inválido en FIREBASE_CREDENTIALS: {e}")
    try:
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        print("Firebase inicializado correctamente.")
    except Exception as e:
        raise ValueError(f"Error al inicializar Firebase: {e}")

# Ruta para enviar notificaciones
@app.route('/send-notification', methods=['POST'])
def send_notification():
    try:
        data = request.get_json()

        # Validar que los campos requeridos estén presentes
        if not data or 'token' not in data or 'title' not in data or 'body' not in data:
            return jsonify({"success": False, "error": "Faltan campos requeridos: token, title o body"}), 400

        # Obtener los datos del JSON
        token = data['token']
        title = data['title']
        body = data['body']

        # Crear el mensaje de notificación
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            token=token
        )

        # Enviar la notificación
        response = messaging.send(message)
        print(f"Notificación enviada: {response}")
        return jsonify({"success": True, "message_id": response})
    except Exception as e:
        print(f"Error al enviar la notificación: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# Inicializar Firebase al iniciar la aplicación
try:
    initialize_firebase()
except Exception as e:
    print(f"Error crítico al inicializar Firebase: {e}")
    exit(1)

# Iniciar la aplicación Flask
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Usa el puerto de Render o 10000 por defecto
    app.run(host='0.0.0.0', port=port)
