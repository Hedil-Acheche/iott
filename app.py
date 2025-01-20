from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
import qrcode
import os
from geopy.distance import geodesic
import requests
import json

# Clé serveur FCM (remplacez par votre clé)
server_key = "YOUR_FCM_SERVER_KEY"

app = Flask(__name__)
socketio = SocketIO(app)

# Liste des objets/monuments avec leurs coordonnées et informations
locations = [
    {
        "id": 1,
        "name": "Musée Historique",
        "latitude": 35.6895,
        "longitude": 139.6917,
        "description": "Un musée fascinant avec des artefacts anciens.",
        "video_url": "static/videos/museum.mp4"
    },
    {
        "id": 2,
        "name": "Monument Ancien",
        "latitude": 35.6845,
        "longitude": 139.6920,
        "description": "Un monument ancien avec une histoire riche.",
        "video_url": "static/videos/monument.mp4"
    }
]

# Assurer que le dossier pour les QR Codes existe
os.makedirs("qr_codes", exist_ok=True)
@socketio.on('connect')
def handle_connect():
    print("Client connecté.")

@app.route('/notify', methods=['POST'])
def notify():
    socketio.emit('notification', {"message": "Proximité détectée !"})
    return jsonify({"message": "Notification envoyée"}), 200

# Page d'accueil avec la liste des monuments
@app.route('/')
def index():
    return render_template("index.html", locations=locations)

# Générer un QR Code pour un monument spécifique
@app.route('/generate_qr/<int:location_id>')
def generate_qr(location_id):
    location = next((loc for loc in locations if loc["id"] == location_id), None)
    if not location:
        return "Lieu non trouvé.", 404

    # Générer le QR code pointant vers la page du monument
    qr = qrcode.make(f"http://127.0.0.1:5000/location/{location_id}")
    qr_path = f"qr_codes/{location_id}.png"
    qr.save(qr_path)
    return send_file(qr_path, mimetype='image/png')

# Page d'un monument spécifique
@app.route('/location/<int:location_id>')
def location(location_id):
    location = next((loc for loc in locations if loc["id"] == location_id), None)
    if not location:
        return "Lieu non trouvé.", 404
    return render_template("location.html", location=location)

# API pour vérifier la proximité et envoyer une notification
@app.route('/check_proximity', methods=['POST'])
def check_proximity():
    user_lat = float(request.json.get("lat"))
    user_lon = float(request.json.get("lon"))

    # Vérifier la distance entre l'utilisateur et les monuments
    for location in locations:
        distance = geodesic((user_lat, user_lon), (location["latitude"], location["longitude"])).km
        if distance < 0.5:  # Rayon de 500m
            send_notification(location)  # Envoyer une notification
            return jsonify(location)  # Retourner les détails du lieu détecté

    return jsonify({"message": "Aucun lieu détecté à proximité."})

# Fonction pour envoyer une notification via FCM
def send_notification(location):
    # Message de notification
    message = {
        "title": f"Proximité détectée : {location['name']}",
        "body": f"Vous êtes proche de {location['name']}. Scannez le QR code pour en savoir plus !",
        "click_action": f"http://127.0.0.1:5000/location/{location['id']}"
    }

    # Exemple d'ID de registration (à remplacer par le vrai ID utilisateur)
    registration_id = "USER_DEVICE_REGISTRATION_ID"

    headers = {
        'Authorization': f'key={server_key}',
        'Content-Type': 'application/json',
    }

    payload = {
        'to': registration_id,
        'notification': {
            'title': message['title'],
            'body': message['body'],
        },
        'data': {
            'click_action': message['click_action']
        }
    }

    # Envoyer la requête à Firebase
    response = requests.post('https://fcm.googleapis.com/fcm/send', headers=headers, data=json.dumps(payload))
    print("Notification envoyée :", response.json())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
