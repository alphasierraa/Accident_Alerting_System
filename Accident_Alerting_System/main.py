import time
import requests
from twilio.rest import Client

def get_ip_address():
    """Get the public IP address of the device."""
    try:
        response = requests.get('https://api.ipify.org?format=json')
        response.raise_for_status()
        data = response.json()
        return data.get('ip')
    except Exception as e:
        print(f"Failed to get IP address: {e}")
        return None

def get_address_from_ip(ip_address, api_key):
    """Get address using IPinfo API."""
    if not ip_address:
        print("IP address is not available. Cannot retrieve address.")
        return None

    url = f'https://ipinfo.io/{ip_address}/json'
    headers = {
        'Authorization': f'Bearer {api_key}'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        city = data.get('city', '')
        region = data.get('region', '')
        country = data.get('country', '')
        return f"{city}, {region}, {country}"
    except Exception as e:
        print(f"Failed to get address from IP: {e}")
        return None

def get_coordinates(address, api_key):
    """Get coordinates using OpenCage Geocoding API."""
    if not address:
        print("Address is empty. Cannot retrieve coordinates.")
        return None, None

    url = 'https://api.opencagedata.com/geocode/v1/json'
    params = {
        'q': address,
        'key': api_key
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        results = data.get('results', [])
        if results:
            location = results[0]['geometry']
            return location['lat'], location['lng']
        return None, None
    except Exception as e:
        print(f"Failed to get location: {e}")
        return None, None

def send_sms(message, address, api_key):
    """Send SMS notification with location details."""
    account_sid = 'AC3e7b43014fef891faec1a0c1fee1ade5'
    auth_token = '222531a6cedd7cf8e1a4f5b321c59cc9'
    sender_number = '+12677047043'  # Twilio phone number
    receiver_number = '+919354082061'  # Recipient's phone number

    # Initialize Twilio client
    client = Client(account_sid, auth_token)

    try:
        # Get coordinates
        lat, lng = get_coordinates(address, api_key)
        if lat is not None and lng is not None:
            location_message = f"Coordinates: Latitude {lat}, Longitude {lng}"
        else:
            location_message = "Unable to retrieve location coordinates."

        # Send SMS message
        message_body = f"{message}\n{location_message}"
        client.messages.create(
            body=message_body,
            from_=sender_number,
            to=receiver_number
        )
        print("SMS notification sent successfully!")
    except Exception as e:
        print(f"Failed to send SMS notification: {e}")

def check_speed(initial_speed, ipinfo_api_key, opencage_api_key):
    """Continuously monitors car speed and sends a warning SMS if it drops suddenly.

    Args:
        initial_speed: The initial speed of the car in kilometers per hour (kmph).
        ipinfo_api_key: IPinfo API key.
        opencage_api_key: OpenCage API key.
    """

    current_speed = initial_speed
    time_t = 0

    while True:
        time_t += 1
        new_speed = float(input("Enter the current speed (kmph): "))

        # Get location if speed drops suddenly
        if new_speed < current_speed - 40:
            ip_address = get_ip_address()
            address = get_address_from_ip(ip_address, ipinfo_api_key) if ip_address else "Unknown location"
            if not address.strip():
                print("No address provided. Cannot send SMS.")
                continue
            warning_message = "WARNING: Speed dropped suddenly by more than 40kmph!"
            print(warning_message)
            send_sms(warning_message, address, opencage_api_key)

        current_speed = new_speed

        # Simulate time passage (replace with actual speed monitoring logic)
        print(f"Time: {time_t} seconds, Speed: {current_speed} kmph")

# Get initial speed from user
initial_speed = float(input("Enter the initial speed of the car (kmph): "))

# API keys
ipinfo_api_key = '97595cdd33182e'
opencage_api_key = '59804b3611e241b7ba86befd9ff71eb8'

check_speed(initial_speed, ipinfo_api_key, opencage_api_key)