import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import firebase_admin
from firebase_admin import credentials, firestore

# Step 1: Initialize Firebase with your service account key
cred = credentials.Certificate("/Users/pien/SHAREDMINDSFALL2024/finals/serviceAccountKey.json")  # Replace with your service account key path
firebase_admin.initialize_app(cred)

# Step 2: Connect to Firestore
db = firestore.client()

# Step 3: Define the function for similarity search
def find_similar_images(clicked_object_id, top_k=11):
    # Fetch the clicked image's embedding
    doc_ref = db.collection("theMet").document(str(clicked_object_id))
    clicked_image_doc = doc_ref.get()
    if not clicked_image_doc.exists:
        print(f"Artwork with ID {clicked_object_id} not found.")
        return []

    clicked_image_data = clicked_image_doc.to_dict()
    clicked_embedding = np.array(clicked_image_data['embedding']).reshape(1, -1)

    # Fetch all artworks with embeddings from Firestore
    artworks_ref = db.collection("theMet")
    docs = artworks_ref.stream()

    embeddings = []
    artwork_ids = []

    for doc in docs:
        artwork_data = doc.to_dict()
        if "embedding" in artwork_data:
            if artwork_data['objectID'] != clicked_object_id:  # Ignore the clicked image itself
                embeddings.append(artwork_data["embedding"])
                artwork_ids.append(artwork_data["objectID"])

    # Convert embeddings to a numpy array
    embeddings_array = np.array(embeddings)

    # Step 4: Calculate cosine similarity
    similarities = cosine_similarity(clicked_embedding, embeddings_array)[0]

    # Step 5: Get indices of the top_k most similar images
    similar_indices = np.argsort(similarities)[-top_k:][::-1]  # Sort in descending order

    # Step 6: Retrieve the artwork metadata for the similar images
    similar_artworks = [artwork_ids[idx] for idx in similar_indices]

    return similar_artworks

# Example usage: Find 11 most similar images for a given artwork ID
clicked_image_id = "201592"  # Replace with the objectID of the clicked image
similar_images = find_similar_images(clicked_image_id)

print(f"Most similar images to artwork {clicked_image_id}: {similar_images}")
