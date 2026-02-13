"""
Ingredient embeddings using Sentence-Transformers
Pre-trained model for semantic similarity of ingredients
"""
from sentence_transformers import SentenceTransformer
import numpy as np
import os
import pickle


# Global model instance
_model = None
_embeddings_cache = {}


def get_model():
    """
    Get or load the Sentence-Transformer model
    
    Returns:
        SentenceTransformer model
    """
    global _model
    
    if _model is None:
        print("Loading Sentence-Transformer model (all-MiniLM-L6-v2)...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Model loaded successfully!")
    
    return _model


def encode_ingredients(ingredients_list):
    """
    Encode a list of ingredient strings into embeddings
    
    Args:
        ingredients_list: List of ingredient strings
    
    Returns:
        numpy array of embeddings (shape: [n_recipes, embedding_dim])
    """
    model = get_model()
    
    # Clean and prepare ingredients
    cleaned_ingredients = []
    for ingredients in ingredients_list:
        if isinstance(ingredients, str):
            cleaned_ingredients.append(ingredients)
        else:
            cleaned_ingredients.append(str(ingredients))
    
    # Encode
    embeddings = model.encode(cleaned_ingredients, show_progress_bar=True)
    
    return embeddings


def compute_similarity(embedding1, embedding2):
    """
    Compute cosine similarity between two embeddings
    
    Args:
        embedding1: First embedding (1D array)
        embedding2: Second embedding (1D or 2D array)
    
    Returns:
        Similarity score(s)
    """
    from sklearn.metrics.pairwise import cosine_similarity
    
    # Ensure 2D arrays
    if embedding1.ndim == 1:
        embedding1 = embedding1.reshape(1, -1)
    
    if embedding2.ndim == 1:
        embedding2 = embedding2.reshape(1, -1)
    
    return cosine_similarity(embedding1, embedding2)


def save_embeddings(embeddings, filepath):
    """
    Save embeddings to disk for future use
    
    Args:
        embeddings: numpy array of embeddings
        filepath: Path to save file
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'wb') as f:
        pickle.dump(embeddings, f)
    print(f"Embeddings saved to {filepath}")


def load_embeddings(filepath):
    """
    Load embeddings from disk
    
    Args:
        filepath: Path to embeddings file
    
    Returns:
        numpy array of embeddings or None if file doesn't exist
    """
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            embeddings = pickle.load(f)
        print(f"Embeddings loaded from {filepath}")
        return embeddings
    return None


def get_or_compute_embeddings(ingredients_list, cache_path=None):
    """
    Get embeddings from cache or compute if not cached
    
    Args:
        ingredients_list: List of ingredient strings
        cache_path: Optional path to cache file
    
    Returns:
        numpy array of embeddings
    """
    # Try to load from cache
    if cache_path and os.path.exists(cache_path):
        embeddings = load_embeddings(cache_path)
        if embeddings is not None and len(embeddings) == len(ingredients_list):
            return embeddings
    
    # Compute embeddings
    print("Computing embeddings...")
    embeddings = encode_ingredients(ingredients_list)
    
    # Save to cache if path provided
    if cache_path:
        save_embeddings(embeddings, cache_path)
    
    return embeddings


def encode_user_profile(user_rated_ingredients):
    """
    Create a user profile embedding based on ingredients from rated recipes
    
    Args:
        user_rated_ingredients: List of ingredient strings from user's rated recipes
    
    Returns:
        Average embedding representing user's ingredient preferences
    """
    if not user_rated_ingredients:
        return None
    
    # Concatenate all ingredients
    combined_ingredients = ' '.join(user_rated_ingredients)
    
    # Encode
    model = get_model()
    user_embedding = model.encode([combined_ingredients])
    
    return user_embedding[0]  # Return 1D array
