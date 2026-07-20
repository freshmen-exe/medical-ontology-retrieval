import pytest
import numpy as np
from vectorbase import VectorBase
from hnsw import HNSW
from bm25 import BM25

# Constants
EMBEDDING_DIM = 1024
SMOOTHING_CONST = 60


# Thêm hằng số scale để khởi tạo các Numba object in-memory
MAX_DOCS_TEST = 100 


@pytest.fixture
def vector_dim() -> int:
    """Trả về số chiều mặc định của vector."""
    return EMBEDDING_DIM


@pytest.fixture
def smoothing_const() -> int:
    """Trả về hằng số smoothing mặc định."""
    return SMOOTHING_CONST


@pytest.fixture
def sample_vector(vector_dim) -> np.ndarray:
    """Sinh một vector ngẫu nhiên đã được chuẩn hóa L2 cho Cosine Metric."""
    vec = np.random.rand(vector_dim).astype(np.float32)
    norm = np.linalg.norm(vec)
    if norm == 0:
        return vec
    return vec / norm


@pytest.fixture
def sample_metadata() -> dict:
    """Sample medical data matching the problem output schema."""
    return {
        "text": "bệnh trào ngược dạ dày - thực quản",
        "type": "CHẨN_ĐOÁN",
        "candidates": ["K21.0", "K21.9"],
        "assertions": ["isHistorical"],
        "position": [82, 121] 
    }

# ======================================
# THIẾT LẬP CÁC FIXTURE CHO NUMBA CORE 
# ======================================

@pytest.fixture
def vector_base(vector_dim) -> VectorBase:
    """Khởi tạo VectorBase object thật với scale siêu nhỏ để test in-memory an toàn."""
    vb = VectorBase(dim=vector_dim, max_n=MAX_DOCS_TEST)
    return vb


@pytest.fixture
def hnsw_db(vector_base) -> HNSW:
    """Khởi tạo HNSW object thật liên kết với VectorBase nhỏ."""
    hnsw = HNSW(vb=vector_base, m=20, efc=200, efs=50, b_sz=100)
    return hnsw


@pytest.fixture
def bm25_db() -> BM25:
    """Khởi tạo BM25 object thật với các tham số cấu hình mặc định."""
    bm25 = BM25(k1=1.5, b=0.75, delta=1.0)
    return bm25


@pytest.fixture
def populated_db(vector_base, hnsw_db, vector_dim):
    """
    Provides a database pre-populated with 10 mock vectors for search testing.
    Đã bổ sung phần thân hàm để thực sự bơm dữ liệu vào VectorBase thật.
    """
    for i in range(10):
        # Sinh vector chuẩn hoá
        vec = np.random.rand(vector_dim).astype(np.float32)
        norm = np.linalg.norm(vec)
        vec_norm = vec / norm if norm > 0 else vec
        
        # Thêm trực tiếp vào object thật để test Numba logic không bị vỡ
        vector_base.vecs[i] = vec_norm
        vector_base.codes[i] = i
    
    vector_base.sz = 10
    return hnsw_db, vector_base

# =====================================================================
# MOCK DATA CHO CÁC LUỒNG XỬ LÝ CAO HƠN
# =====================================================================

@pytest.fixture
def dense_mock() -> tuple[np.ndarray, np.ndarray]:
    """
    Mock kết quả đầu ra từ Dense Search (HNSW) dùng để test luồng Ranker/Pipeline.
    Trả về bộ đôi (dists, ids) khớp với format hàm search() trong hnsw_core.
    """
    # Kịch bản mock: Trả về k=3 kết quả
    dists = np.array([0.15, 0.22, 0.35], dtype=np.float32)
    ids = np.array([1, 2, 5], dtype=np.int32)
    return dists, ids


@pytest.fixture
def sparse_mock() -> np.ndarray:
    """
    Giả lập kết quả trả về từ mô hình BM25 (Sparse Search).
    Chuyển từ Dict sang numpy array (float32) để tương thích với hàm BM25.search().
    """
    # Khởi tạo mảng điểm toàn 0 giống hệt logic trong bm25_core
    scores = np.zeros(MAX_DOCS_TEST, dtype=np.float32)
    
    # Gán điểm giả lập (scores) cho một vài index (doc_ids) cụ thể
    scores[1] = 5.2 # Tương đương ICD code tại index 1
    scores[2] = 1.0 # Tương đương ICD code tại index 2
    scores[4] = 2.1 # Tương đương ICD code tại index 4
    
    return scores