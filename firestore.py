import firebase_admin
from firebase_admin import credentials, firestore
import json

# Step 1: Initialize Firebase with your service account key
cred = credentials.Certificate("/Users/pien/SHAREDMINDSFALL2024/finals/serviceAccountKey.json")  # Replace with the correct path to your key file
firebase_admin.initialize_app(cred)

# Step 2: Connect to Firestore
db = firestore.client()

# Step 3: Load Artwork Data from JSON
with open("/Users/pien/SHAREDMINDSFALL2024/finals/met_public_domain_details.json", "r") as file:
    artworks = json.load(file)

# Step 4: Upload Each Artwork to Firestore under the collection "theMet"
for artwork in artworks:
    # Use objectID as the document ID to ensure each artwork is unique
    doc_ref = db.collection("theMet").document(str(artwork['objectID']))
    doc_ref.set(artwork)  # Upload artwork data as the document content
    print(f"Uploaded artwork: {artwork['title']}")

print(f"Successfully uploaded {len(artworks)} artworks to Firestore.")
