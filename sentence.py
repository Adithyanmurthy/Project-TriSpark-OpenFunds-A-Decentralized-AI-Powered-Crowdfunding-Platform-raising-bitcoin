from sentence_transformers import SentenceTransformer
# This will download the model if it doesn't exist
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model downloaded successfully!")
