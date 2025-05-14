# Deep Learning-based Similar Campaign Recommender for OpenFunds

from sentence_transformers import SentenceTransformer, util
import pandas as pd
import os
import torch
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
CSV_PATH = "data_exports/campaigns.csv"
MODEL_NAME = 'all-MiniLM-L6-v2'

# Initialize model globally to avoid reloading
try:
    model = SentenceTransformer(MODEL_NAME)
    logger.info(f"Model {MODEL_NAME} loaded successfully")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    model = None

# Get Similar Campaigns Based on Text Similarity
def get_similar_campaigns(title, description, top_k=3, threshold=0.3):
    """
    Find similar campaigns based on title and description.
    Returns list of dicts with title, description, and similarity score.
    """
    # Ensure model is loaded
    global model
    if model is None:
        try:
            model = SentenceTransformer(MODEL_NAME)
            logger.info("Model loaded on-demand")
        except Exception as e:
            logger.error(f"Failed to load model on-demand: {e}")
            return []

    # Check for CSV file
    if not os.path.exists(CSV_PATH):
        logger.warning(f"CSV file not found at {CSV_PATH}")
        return []

    try:
        # Read campaigns
        df = pd.read_csv(CSV_PATH)
        
        # Return empty if no campaigns
        if df.empty:
            logger.info("CSV file exists but is empty")
            return []
            
        # Log number of campaigns found
        logger.info(f"Found {len(df)} campaigns in CSV")

        # Prepare inputs
        df['text'] = df['title'].astype(str) + " " + df['description'].astype(str)
        input_text = title + " " + description

        # Encode existing campaigns
        logger.info("Encoding campaign texts...")
        corpus_embeddings = model.encode(df['text'].tolist(), convert_to_tensor=True)
        
        # Encode input
        input_embedding = model.encode(input_text, convert_to_tensor=True)

        # Compute similarity
        logger.info("Computing similarity...")
        cos_scores = util.pytorch_cos_sim(input_embedding, corpus_embeddings)[0]
        
        # Convert to regular Python list
        scores = cos_scores.cpu().tolist()

        # Build response with indices and scores
        results = []
        for idx, score in enumerate(scores):
            # Only include sufficiently similar campaigns
            if score > threshold:
                row = df.iloc[idx]
                results.append({
                    'title': row['title'],
                    'description': row['description'],
                    'score': score
                })
        
        # Sort by similarity score (highest first) and take top_k
        results = sorted(results, key=lambda x: x['score'], reverse=True)[:top_k]
        
        logger.info(f"Found {len(results)} similar campaigns")
        return results

    except Exception as e:
        logger.error(f"Error in get_similar_campaigns: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []

# Update Embeddings (not needed during prediction, only if extending feature)
def update_embeddings():
    """Update embeddings for all campaigns in the CSV."""
    if not os.path.exists(CSV_PATH):
        logger.warning(f"CSV file not found at {CSV_PATH} - cannot update embeddings")
        return

    try:
        # Ensure model is loaded
        global model
        if model is None:
            model = SentenceTransformer(MODEL_NAME)
            
        df = pd.read_csv(CSV_PATH)
        if df.empty:
            logger.info("No campaigns to update embeddings for")
            return
            
        texts = (df['title'].astype(str) + " " + df['description'].astype(str)).tolist()
        logger.info(f"Updating embeddings for {len(texts)} campaigns")
        
        # Generate embeddings
        embeddings = model.encode(texts, convert_to_tensor=True)
        
        logger.info("Embeddings updated successfully")
        return embeddings

    except Exception as e:
        logger.error(f"Error updating embeddings: {e}")
        return None

# If run as script, test the model loading
if __name__ == "__main__":
    print(f"Testing model loading: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    print("Model loaded successfully!")
    
    # Test encoding
    test_embedding = model.encode("Test campaign", convert_to_tensor=True)
    print(f"Test encoding shape: {test_embedding.shape}")
    print("All tests passed!")