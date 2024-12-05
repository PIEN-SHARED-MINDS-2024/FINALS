import firebase_admin
from firebase_admin import credentials, firestore
import json

# Step 1: Initialize Firebase with your existing service account key
cred = credentials.Certificate("/Users/pien/SHAREDMINDSFALL2024/finals/serviceAccountKey.json")  # Reuse the existing key file
firebase_admin.initialize_app(cred)

# Step 2: Connect to Firestore
db = firestore.client()

# Step 3: Load Artwork Data from JSON (Artsy data file)
with open("/Users/pien/SHAREDMINDSFALL2024/finals/artsy_public_domain_details.json", "r") as file:
    artworks = json.load(file)

# Step 4: Upload Each Artwork to Firestore under the collection "artsy"
for artwork in artworks:
    # Ensure that the artwork has an image URL
    if not artwork.get("imageUrl"):
        print(f"Skipping artwork without image: {artwork.get('title', 'Unknown')}")
        continue

    # Use objectID as the document ID to ensure each artwork is unique
    doc_ref = db.collection("artsy").document(str(artwork['objectID']))
    # Upload artwork data as the document content
    doc_ref.set(artwork)
    print(f"Uploaded artwork: {artwork['title']}")

print(f"Successfully uploaded {len(artworks)} artworks to Firestore.")
