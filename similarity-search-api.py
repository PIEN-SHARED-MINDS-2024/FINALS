from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Apply CORS to all routes to allow cross-origin requests from any origin

# Initialize Firebase
cred = credentials.Certificate("/Users/pien/SHAREDMINDSFALL2024/finals/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Normalization function to standardize data fields from both collections
def normalize_data(artwork_data):
    return {
        "objectID": artwork_data.get("objectID") or artwork_data.get("id"),
        "imageUrl": artwork_data.get("imageUrl") or artwork_data.get("image_url"),
        "embedding": artwork_data.get("embedding")
    }

def find_similar_images(clicked_object_id, collection, top_k=16):
    try:
        print(f"Finding similar images for objectID: {clicked_object_id} from collection: {collection}")
        
        # Convert the clicked object ID to a string
        clicked_object_id = str(clicked_object_id)

        # Determine the collection to search
        if collection == "all":
            collections_to_search = ["theMet", "artsy"]
        else:
            collections_to_search = [collection]

        # Fetch the clicked image's embedding
        clicked_image_doc = None
        for col in collections_to_search:
            print(f"Searching collection: {col}")
            doc_ref = db.collection(col).document(clicked_object_id)
            clicked_image_doc = doc_ref.get()
            if clicked_image_doc.exists:
                break

        if not clicked_image_doc or not clicked_image_doc.exists:
            print(f"Artwork with ID {clicked_object_id} not found in any collection.")
            return []

        clicked_image_data = normalize_data(clicked_image_doc.to_dict())

        if "embedding" not in clicked_image_data or clicked_image_data["embedding"] is None:
            print(f"Embedding not found for artwork ID {clicked_object_id}.")
            return []

        clicked_embedding = np.array(clicked_image_data['embedding']).reshape(1, -1)

        # Fetch all artworks with embeddings from Firestore
        embeddings = []
        artwork_ids = []

        for col in collections_to_search:
            print(f"Fetching artworks with embeddings from collection: {col}")
            artworks_ref = db.collection(col)
            docs = artworks_ref.stream()

            for doc in docs:
                artwork_data = normalize_data(doc.to_dict())
                
                if artwork_data["embedding"] and artwork_data["objectID"] and artwork_data["objectID"] != clicked_object_id:
                    embeddings.append(artwork_data["embedding"])
                    artwork_ids.append(artwork_data["objectID"])

        if len(embeddings) == 0:
            print("No embeddings found for comparison.")
            return []

        # Convert embeddings to a numpy array
        embeddings_array = np.array(embeddings)

        # Calculate cosine similarity
        similarities = cosine_similarity(clicked_embedding, embeddings_array)[0]

        # Get indices of the top_k most similar images
        similar_indices = np.argsort(similarities)[-top_k:][::-1]  # Sort in descending order

        # Retrieve the artwork metadata for the similar images
        similar_artworks = [str(artwork_ids[idx]) for idx in similar_indices]

        print(f"Found {len(similar_artworks)} similar artworks.")
        return similar_artworks
    except Exception as e:
        print(f"Error in find_similar_images: {e}")
        return []

@app.route('/find_similar', methods=['POST'])
def find_similar():
    try:
        data = request.get_json()
        print("Received request data:", data)

        clicked_object_id = data.get("objectID")
        collection = data.get("collection")

        if not clicked_object_id or not collection:
            print("Missing required fields: objectID or collection")
            return jsonify({"error": "Missing required fields (objectID or collection)"}), 400

        # Convert clicked_object_id to string for consistency
        clicked_object_id = str(clicked_object_id)

        # Proceed with finding similar images
        similar_images = find_similar_images(clicked_object_id, collection)

        if not similar_images:
            return jsonify({"message": "No similar artworks found"}), 404

        return jsonify({"similar_artworks": similar_images})

    except Exception as e:
        print("Error processing request:", str(e))
        return jsonify({"error": str(e)}), 500
