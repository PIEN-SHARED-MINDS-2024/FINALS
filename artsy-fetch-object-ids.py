import requests
import json
import firebase_admin
from firebase_admin import credentials, firestore
import os

# Function to fetch a new access token
def get_access_token():
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
        return response.json()["token"]
    else:
        raise Exception(f"Failed to obtain token. Status Code: {response.status_code}, {response.text}")

# Step 1: Get a valid access token
access_token = get_access_token()

# Initialize Firebase Admin SDK
cred = credentials.Certificate("/Users/pien/SHAREDMINDSFALL2024/finals/serviceAccountKey.json")  # Update with your Firebase Admin SDK JSON file path
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Step 2: Load existing artwork IDs from JSON file
json_file_path = "/Users/pien/SHAREDMINDSFALL2024/finals/artsy_public_domain_ids.json"
existing_ids = set()

if os.path.exists(json_file_path):
    with open(json_file_path, "r") as json_file:
        try:
            existing_ids = set(json.load(json_file))
        except json.JSONDecodeError:
            print("The JSON file is empty or contains invalid data, starting with an empty set.")
else:
    print("No existing JSON file found, creating a new one.")

# Step 3: Fetch Artwork IDs from Artsy API
url = "https://api.artsy.net/api/artworks"
headers = {
    "X-Xapp-Token": access_token,
    "Accept": "application/vnd.artsy-v2+json"
}

fetched_object_ids = []
params = {"size": 1000}  # Adjust size as needed

response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()
    artworks = data.get('_embedded', {}).get('artworks', [])

    if not artworks:
        print("No artworks found.")
    else:
        # Add new IDs to the list, avoiding duplicates
        fetched_object_ids = [artwork['id'] for artwork in artworks if artwork['id'] not in existing_ids]
        print(f"Fetched {len(fetched_object_ids)} artwork IDs.")
else:
    print(f"Failed to fetch artwork IDs. Status Code: {response.status_code}")
    print(f"Response Content: {response.text}")

# Step 4: Save the fetched IDs to JSON file for documentation
combined_ids = list(existing_ids.union(fetched_object_ids))

with open(json_file_path, "w") as json_file:
    json.dump(combined_ids, json_file, indent=2)
print(f"Saved {len(combined_ids)} artwork IDs to '{json_file_path}'.")

# Step 5: Fetch details for each artwork and upload to Firebase
for artwork_id in fetched_object_ids:
    # Check if the artwork already exists in Firestore
    if db.collection('artsy').document(artwork_id).get().exists:
        print(f"Artwork ID {artwork_id} already exists in Firestore. Skipping.")
        continue

    # Fetch the detailed metadata for the artwork
    detail_url = f"https://api.artsy.net/api/artworks/{artwork_id}"
    detail_response = requests.get(detail_url, headers=headers)

    if detail_response.status_code == 200:
        artwork_details = detail_response.json()

        # Replace {image_version} with a specific version in image URLs
        if "_links" in artwork_details and "image" in artwork_details["_links"]:
            image_href = artwork_details["_links"]["image"]["href"]
            image_url = image_href.replace("{image_version}", "large")
            artwork_details["image_url"] = image_url

            # Also update the "href" field inside the "image" map
            artwork_details["_links"]["image"]["href"] = image_url

        # Upload artwork details to Firebase 'artsy' collection
        db.collection('artsy').document(artwork_id).set(artwork_details)
        print(f"Uploaded artwork details for ID {artwork_id} to Firebase")
    else:
        print(f"Failed to fetch details for artwork ID: {artwork_id}. Status Code: {detail_response.status_code}")
        print(f"Response Content: {detail_response.text}")
