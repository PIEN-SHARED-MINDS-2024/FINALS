import requests
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

# Step 3: Fetch the specific artwork by ID
artwork_id = "515b0832223afae9a5000081"
doc_ref = db.collection('artsy').document(artwork_id)
doc = doc_ref.get()

if not doc.exists:
    print(f"Document with ID {artwork_id} does not exist.")
else:
    artwork_data = doc.to_dict()

    # Check if the document already has an embedding
    if "embedding" in artwork_data:
        print(f"Artwork ID {artwork_id} already has an embedding. No update required.")
    else:
        image_url = artwork_data.get("image_url")
        if not image_url:
            print(f"No image URL found for artwork ID {artwork_id}. Skipping.")
        else:
            # Step 4: Download the Image
            try:
                response = requests.get(image_url)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content)).convert("RGB")

                # Step 5: Preprocess the Image and Generate Embedding
                inputs = processor(images=image, return_tensors="pt").to(device)
                with torch.no_grad():
                    image_features = model.get_image_features(**inputs)
                    embedding = image_features.cpu().numpy().flatten().tolist()

                # Step 6: Update Firestore Document with Embedding
                doc_ref.update({"embedding": embedding})
                print(f"Uploaded embedding for artwork ID {artwork_id} to Firebase")

            except requests.RequestException as e:
                print(f"Failed to download image for artwork ID {artwork_id}. Error: {e}")
            except Exception as e:
                print(f"Failed to generate or store embedding for artwork ID {artwork_id}. Error: {e}")
