import firebase_admin
from firebase_admin import credentials, firestore
import clip
import torch
from PIL import Image
import requests
from io import BytesIO
import json
import time

# Step 1: Initialize Firebase with your service account key
cred = credentials.Certificate("/Users/pien/SHAREDMINDSFALL2024/finals/serviceAccountKey.json")  # Replace with your service account key path
firebase_admin.initialize_app(cred)

# Step 2: Connect to Firestore
db = firestore.client()

# Step 3: Load CLIP Model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# Step 4: Load Processed IDs from Checkpoint File
processed_ids = set()
try:
    with open("/Users/pien/SHAREDMINDSFALL2024/finals/processed_ids.txt", "r") as f:
        processed_ids = set(line.strip() for line in f)
    print(f"Loaded {len(processed_ids)} processed IDs from checkpoint file.")
except FileNotFoundError:
    print("Checkpoint file not found. Starting fresh...")

# Step 5: Retrieve Artwork Data in Batches to Avoid Deadline Errors
page_size = 100  # Number of documents to retrieve per batch
artworks_ref = db.collection("theMet")
current_query = artworks_ref.limit(page_size)

batch_number = 1
total_updated = 0

while True:
    print(f"Fetching batch {batch_number} of {page_size} artworks...")
    documents = current_query.stream()

    last_doc = None
    batch_processed = 0

    for artwork in documents:
        last_doc = artwork
        artwork_data = artwork.to_dict()

        # Ensure 'objectID' key is present
        if 'objectID' not in artwork_data:
            print(f"[Batch {batch_number}] Skipping artwork (Missing 'objectID' key)")
            continue

        object_id = str(artwork_data['objectID'])

        # Skip if artwork has already been processed
        if object_id in processed_ids:
            print(f"[Batch {batch_number}] Skipping artwork {artwork_data.get('title', 'Unknown')} (Already processed)")
            continue

        image_url = artwork_data.get("imageUrl")

        if not image_url:
            print(f"[Batch {batch_number}] Skipping artwork {artwork_data.get('title', 'Unknown')} (No image URL available)")
            continue

        # Step 6: Load the image from the URL
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
        except Exception as e:
            print(f"[Batch {batch_number}] Failed to load image for artwork {artwork_data.get('title', 'Unknown')}: {e}")
            continue

        # Step 7: Preprocess the image and generate the embedding
        try:
            image_input = preprocess(image).unsqueeze(0).to(device)
            with torch.no_grad():
                image_features = model.encode_image(image_input)

            # Convert to a vector that can be stored in Firestore
            embedding = image_features.cpu().numpy().flatten().astype(float).tolist()
        except Exception as e:
            print(f"[Batch {batch_number}] Failed to generate embedding for artwork {artwork_data.get('title', 'Unknown')}: {e}")
            continue

        # Step 8: Update Firestore document with the embedding
        doc_ref = artworks_ref.document(object_id)
        try:
            doc_ref.update({"embedding": embedding})
            print(f"[Batch {batch_number}] Updated artwork: {artwork_data['title']} with embedding")
            
            # Save progress by appending to the checkpoint file
            with open("/Users/pien/SHAREDMINDSFALL2024/finals/processed_ids.txt", "a") as f:
                f.write(object_id + "\n")

            # Add to processed_ids to avoid duplication during current run
            processed_ids.add(object_id)
            batch_processed += 1
            total_updated += 1
        except Exception as e:
            print(f"[Batch {batch_number}] Failed to update artwork {artwork_data['title']}: {e}")

    # Print summary of the current batch
    print(f"Batch {batch_number} processed: {batch_processed} artworks updated successfully.")
    batch_number += 1

    # If no more documents to fetch, break the loop
    if last_doc is None:
        break

    # Move to the next batch
    current_query = artworks_ref.start_after(last_doc).limit(page_size)

# Final summary
print(f"Processing complete. Total artworks updated: {total_updated}")
