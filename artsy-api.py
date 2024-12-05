import requests
import json

# Step 1: Generate the Access Token
client_id = '872241fde23e69d59e8f'
client_secret = '0b2a7666ad3768f12d290d12d3e6b62d'

token_url = 'https://api.artsy.net/api/tokens/xapp_token'
token_params = {
    'client_id': client_id,
    'client_secret': client_secret
}

response = requests.post(token_url, data=token_params)

if response.status_code == 201:
    token_data = response.json()
    access_token = token_data['token']
    print(f"Access Token: {access_token}")
else:
    print(f"Failed to get access token. Status Code: {response.status_code}")
    exit()
