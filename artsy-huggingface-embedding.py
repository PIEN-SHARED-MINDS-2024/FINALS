import requests
import json
import firebase_admin
from firebase_admin import credentials, firestore
from PIL import Image
from io import BytesIO
import torch
from transformers import CLIPProcessor, CLIPModel

# Step 1: Initialize Firebase Admin SDK
cred = credentials.Certificate("/Users/pien/SHAREDMINDSFALL2024/finals/serviceAccountKey.json")  # Update with your Firebase Admin SDK JSON file path
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Step 2: Load Hugging Face CLIP Model
device = "cuda" if torch.cuda.is_available() else "cpu"
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Step 3: Fetch Artwork Data from Firestore
artsy_collection = db.collection('artsy')
artwork_docs = artsy_collection.stream()

for doc in artwork_docs:
    artwork_data = doc.to_dict()
    artwork_id = doc.id
    image_url = artwork_data.get("image_url")

    # Check if the artwork already has an embedding
    if "embedding" in artwork_data:
        print(f"Artwork ID {artwork_id} already has an embedding. Skipping.")
        continue

    if not image_url:
        print(f"No image URL found for artwork ID {artwork_id}. Skipping.")
        continue

    # Step 4: Download the Image
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content)).convert("RGB")
    except requests.RequestException as e:
        print(f"Failed to download image for artwork ID {artwork_id}. Error: {e}")
        continue

    # Step 5: Preprocess the Image and Generate Embedding
    try:
        inputs = processor(images=image, return_tensors="pt").to(device)
        with torch.no_grad():
            image_features = model.get_image_features(**inputs)
            embedding = image_features.cpu().numpy().flatten().tolist()

        # Step 6: Update Firestore Document with Embedding
        artsy_collection.document(artwork_id).update({"embedding": embedding})
        print(f"Uploaded embedding for artwork ID {artwork_id} to Firebase")

    except Exception as e:
        print(f"Failed to generate or store embedding for artwork ID {artwork_id}. Error: {e}")

print("All embeddings have been processed.")
