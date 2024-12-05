import requests
import json

# Step 1: Load existing object IDs to avoid duplicates
try:
    with open("/Users/pien/SHAREDMINDSFALL2024/finals/met_public_domain_ids.json", "r") as file:
        existing_object_ids = set(json.load(file))
except FileNotFoundError:
    # If the file does not exist, start with an empty set
    existing_object_ids = set()

# Fetch new object IDs from The Met API
url = "https://collectionapi.metmuseum.org/public/collection/v1/search"
params = {
    "isPublicDomain": "true",  # Only public domain items
    "q": "painting"  # Use a general search term to get results
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    if 'objectIDs' in data and data['objectIDs']:
        # Filter out IDs that already exist in our set
        new_object_ids = [obj_id for obj_id in data['objectIDs'] if obj_id not in existing_object_ids]
        # Limit to the first 1000 new IDs for manageability
        new_object_ids = new_object_ids[:1000]
        print(f"Fetched {len(new_object_ids)} new public domain object IDs.")
    else:
        print("No new public domain object IDs found.")
        new_object_ids = []
else:
    print(f"Failed to fetch public domain object IDs. Status code: {response.status_code}")
    exit()

# Combine existing and new object IDs
combined_object_ids = list(existing_object_ids) + new_object_ids

# Save the combined list of object IDs to the JSON file
with open("/Users/pien/SHAREDMINDSFALL2024/finals/met_public_domain_ids.json", "w") as file:
    json.dump(combined_object_ids, file)

print("Saved updated public domain object IDs to 'met_public_domain_ids.json'")
