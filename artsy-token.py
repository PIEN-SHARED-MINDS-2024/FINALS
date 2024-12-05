import requests

client_id = "872241fde23e69d59e8f"
client_secret = "0b2a7666ad3768f12d290d12d3e6b62d"

response = requests.post(
    "https://api.artsy.net/api/tokens/xapp_token",
    data={
        "client_id": client_id,
        "client_secret": client_secret
    }
)

if response.status_code == 201:
    xapp_token = response.json()["token"]
    print("XAPP Token:", xapp_token)
else:
    print("Failed to obtain token")
    print(response.status_code, response.text)

