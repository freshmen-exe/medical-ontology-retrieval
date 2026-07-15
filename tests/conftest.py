import pytest
import numpy as np


#Change this if the embedding model using other number of dimension
EMBEDDING_DIM = 384

@pytest.fixture
def vector_dim():

    return EMBEDDING_DIM


@pytest.fixture
def sample_vector():

    """ Generate a random valid vector of the correct dimension"""
    return np.random.rand(EMBEDDING_DIM).astype(np.float32)


@pytest.fixture
def sample_metadata():
    "Sample medical data matching the problem output schema"
    return {
        "text": "bệnh trào ngược dạ dày - thực quản",
        "type": "CHẨN_ĐOÁN",
        "candidates": ["K21.0", "K21.9"],
        "assertions": ["isHistorical"],
        "position": [82, 121]  # Added to satisfy the strict invariant
    }


@pytest.fixture
def hnsw_db(vector_dim):

    """
    Initialize an empty vectorbase
    Needing to import the class from the vectorbase implement"
    """

    """
    Here I assume there is a file named 'vectorbase.py' in 'src/'
    and a class named 'Vectorbase'.
    """
    from src.vectorbase import VectorBase

    # Initialize the class and pass it to the tests
    db_instance = Vectorbase(dimension = vector_dim)

    return db_instance


@pytest.fixture
def populated_db(hnsw_db, vector_dim):
    """
    Provides a database pre-populated with 10 mock vectors for search testing.
    """

    # Insert 10 mock vectors with basic metadata
    for vector_id in range(10):
        vector = np.random.rand(vector_dim).astype(np.float32)
        meta = {
            "id" : vector_id,
            "text": f"Mẫu bệnh lý {vector_id}",
            "type": "CHẨN ĐOÁN" if vector_id % 2 == 0 else "TRIỆU CHỨNG",
            "candidates": [],
            "assertions": [],
            "position": [vector_id*13, vector_id*13 + 13]

        }
        hnsw_db.add(vector,meta)

    return hnsw_db
