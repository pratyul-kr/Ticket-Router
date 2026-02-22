from sentence_transformers import SentenceTransformer

# Load the model once when the app starts — not on every request
# all-MiniLM-L6-v2 is small (80MB), fast, and great for semantic similarity
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def get_embedding(text: str) -> list[float]:
    """
    Convert a piece of text into a list of 384 numbers (a vector).
    Similar texts will produce similar vectors.
    """
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()