from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Apply CORS to all routes to allow cross-origin requests from any origin

# Step 1: Initialize Firebase with your service account key
cred = credentials.Certificate("/Users/pien/SHAREDMINDSFALL2024/finals/serviceAccountKey.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Step 2: Connect to Firestore
db = firestore.client()

# Step 3: Define the function for similarity search for different collections
def find_similar_images(collection_name, clicked_object_id, top_k=11):
    try:
        # Fetch the clicked image's embedding
        doc_ref = db.collection(collection_name).document(str(clicked_object_id))
        clicked_image_doc = doc_ref.get()
        if not clicked_image_doc.exists:
            print(f"Artwork with ID {clicked_object_id} not found in collection {collection_name}.")
            return []

        clicked_image_data = clicked_image_doc.to_dict()
        clicked_embedding = np.array(clicked_image_data['embedding']).reshape(1, -1)

        # Fetch all artworks with embeddings from Firestore, excluding the clicked image itself
        docs = db.collection(collection_name).where("embedding", "!=", None).where("objectID", "!=", clicked_object_id).stream()

        embeddings = []
        artwork_ids = []

        for doc in docs:
            artwork_data = doc.to_dict()
            embeddings.append(artwork_data["embedding"])
            artwork_ids.append(artwork_data["objectID"])

        if len(embeddings) == 0:
            print("No embeddings found for comparison.")
            return []

        # Convert embeddings to a numpy array
        embeddings_array = np.array(embeddings)

        # Step 4: Calculate cosine similarity
        similarities = cosine_similarity(clicked_embedding, embeddings_array)[0]

        # Step 5: Get indices of the top_k most similar images
        similar_indices = np.argsort(similarities)[-top_k:][::-1]  # Sort in descending order

        # Step 6: Retrieve the artwork metadata for the similar images
        similar_artworks = [artwork_ids[idx] for idx in similar_indices]

        return similar_artworks
    except Exception as e:
        print(f"Error in find_similar_images: {e}")
        return []

# Step 4: Create an endpoint for similarity search
@app.route('/find_similar', methods=['POST'])
def find_similar():
    try:
        data = request.get_json()
        collection_name = data.get("collection_name")
        clicked_object_id = data.get("objectID")
        top_k = data.get("top_k", 16)  # Default to 16 if not provided

        print(f"Received request to /find_similar with collection_name: {collection_name}, objectID: {clicked_object_id}")

        if not collection_name or not clicked_object_id:
            return jsonify({"error": "No collection_name or objectID provided"}), 400

        similar_images = find_similar_images(collection_name, clicked_object_id, top_k)

        if not similar_images:
            return jsonify({"message": "No similar artworks found"}), 404

        return jsonify({"similar_artworks": similar_images})

    except Exception as e:
        print("Error processing request:", str(e))
        return jsonify({"error": str(e)}), 500

# Step 5: Run the Flask app
if __name__ == '__main__':
    app.run(port=5000, debug=True)
