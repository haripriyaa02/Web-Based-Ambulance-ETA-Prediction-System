from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import smtplib
from geopy.distance import geodesic
from twilio.rest import Client

# Twilio credentials (replace with your actual credentials from Twilio console)
TWILIO_ACCOUNT_SID = 'AC######'
TWILIO_AUTH_TOKEN = 'f969##########'
TWILIO_PHONE_NUMBER = '+132######'  # Your Twilio number

app = Flask(__name__)




# Dummy hospital location
hospital_location = (12.9860, 77.6350)

# Function to estimate ETA (assuming average ambulance speed ~40 km/h)
def estimate_eta(start, end):
    distance = geodesic(start, end).km
    avg_speed_kmh = 40
    eta_minutes = (distance / avg_speed_kmh) * 60
    return round(eta_minutes, 2)

# Simulated message sending
def notify_traffic_police(contact, signal_name, eta):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=f"🚑 Ambulance arriving at {signal_name} in {eta} minutes. Please clear the way.",
        from_=TWILIO_PHONE_NUMBER,
        to=contact
    )
    print(f"Sent message to {contact}: SID = {message.sid}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict_eta', methods=['POST'])
def predict_eta():
    data = request.json
    start = (float(data['start_lat']), float(data['start_lon']))
    end = (float(data['end_lat']), float(data['end_lon']))
    signal_coords = data.get('signals', [])  # list of [lat, lon]

    # Predefined contact numbers for signals
    contact_numbers = [
        "+919361950010",  # For Signal 1
        "+919361950010",  # For Signal 2
        "+919361950010"   # For Signal 3
    ]

    responses = []
    current_point = start

    for i, coords in enumerate(signal_coords):
        signal_loc = tuple(coords)
        eta = estimate_eta(current_point, signal_loc)

        contact = contact_numbers[i] if i < len(contact_numbers) else contact_numbers[-1]  # fallback to last
        signal_name = f"Signal {i+1}"
        notify_traffic_police(contact, signal_name, eta)

        responses.append({
            "signal": signal_name,
            "eta_minutes": eta
        })

        current_point = signal_loc

    # Final ETA to hospital
    eta_to_hospital = estimate_eta(current_point, end)
    responses.append({
        "destination": "Hospital",
        "eta_minutes": eta_to_hospital
    })

    return jsonify(responses)



if __name__ == '__main__':
    app.run(debug=True)
