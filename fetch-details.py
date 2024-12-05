import requests
import json
import time

# Step 1: Load existing artwork details to avoid duplicates
try:
    with open("/Users/pien/SHAREDMINDSFALL2024/finals/met_public_domain_details.json", "r") as file:
        existing_artworks = json.load(file)
        existing_object_ids = {artwork['objectID'] for artwork in existing_artworks}  # Use a set for fast lookup
except FileNotFoundError:
    # If the file does not exist, start with an empty list and set
    existing_artworks = []
    existing_object_ids = set()

# Step 2: Load the list of public domain object IDs (new and existing)
with open("/Users/pien/SHAREDMINDSFALL2024/finals/met_public_domain_ids.json", "r") as file:
    object_ids = json.load(file)

# Initialize a list to store new artwork details
new_artworks = []

# Fetch detailed information for each object ID
for object_id in object_ids:
    # Skip object IDs that have already been downloaded
    if object_id in existing_object_ids:
        print(f"Skipping object ID {object_id} (already processed)")
        continue

    url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"
    response = requests.get(url)

    if response.status_code == 200:
        obj_data = response.json()

        # Ensure that the artwork is public domain and has an image
        if obj_data.get('isPublicDomain') and obj_data.get('primaryImage'):
            artwork = {
                "objectID": obj_data.get('objectID'),
                "title": obj_data.get('title', 'Unknown'),
                "artist": obj_data.get('artistDisplayName', 'Unknown'),
                "imageUrl": obj_data.get('primaryImage'),
                "culture": obj_data.get('culture', 'Unknown'),
                "date": obj_data.get('objectDate', 'Unknown'),
                "medium": obj_data.get('medium', 'Unknown'),
                # Add more fields as needed
            }
            new_artworks.append(artwork)
            print(f"Added: {artwork['title']}")
        else:
            # Print why the artwork was not added
            if not obj_data.get('primaryImage'):
                print(f"Skipping {obj_data.get('title', 'Unknown')} (No primary image)")

    # Respect the API's rate limit by adding a small delay
    time.sleep(0.0125)  # 80 requests per second = 1 request every 0.0125 seconds

# Combine the old and new artwork details
combined_artworks = existing_artworks + new_artworks

# Save the combined artwork details to the JSON file
with open("/Users/pien/SHAREDMINDSFALL2024/finals/met_public_domain_details.json", "w") as outfile:
    json.dump(combined_artworks, outfile)

print(f"Fetched and saved data for {len(new_artworks)} new public domain artworks.")
