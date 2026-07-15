import pytest
import numpy as np

# ==============================
# 1. Normal Dense Search Operations
# ==============================


"""Test 1: Truy vấn với vector y hệt vector trong DB phải trả về khoảng cách Cosine bằng 0 (hoặc rất gần 0)"""
def test_dense_exact_match(hnsw_db, sample_vector):
    
    hnsw_db.add(sample_vector, {"id": "doc_1"})
    
    results = hnsw_db.dense_search(query_vector=sample_vector, top_k=1)
    
    assert len(results) > 0, "Lỗi: Truy vấn exact match không trả về kết quả nào."
    
    assert results[0]["metadata"]["id"] == "doc_1", f"Lỗi: Sai ID kết quả. Kỳ vọng 'doc_1', nhận '{results[0]['metadata']['id']}'."
    
    assert pytest.approx(results[0]["distance"], abs = 1e-5) == 0.0, f"Lỗi: Cosine distance của 2 vector giống hệt nhau phải = 0.0, nhận {results[0]['distance']}."


"""Test 2: Hai vector vuông góc phải có khoảng cách Cosine bằng 1.0 (vì cosine similarity = 0)."""
def test_dense_orthogonal_vectors(hnsw_db, vector_dim):
    
    vec_a = np.zeros(vector_dim, dtype=np.float32)
    vec_a[0] = 1.0  # [1, 0, 0, ...]
    
    vec_b = np.zeros(vector_dim, dtype=np.float32)
    vec_b[1] = 1.0  # [0, 1, 0, ...]
    
    hnsw_db.add(vec_a, {"id": "doc_a"})
    results = hnsw_db.dense_search(query_vector = vec_b, top_k = 1)
    
    assert pytest.approx(results[0]["distance"], abs = 1e-5) == 1.0, f"Lỗi: Cosine distance của 2 vector vuông góc phải = 1.0, nhận {results[0]['distance']}."


"""Test 3: Hai vector đối nghịch nhau phải có khoảng cách Cosine bằng 2.0 (vì cosine similarity = -1)."""
def test_dense_opposite_vectors(hnsw_db, vector_dim):

    vec_a = np.ones(vector_dim, dtype = np.float32)
    vec_b = -np.ones(vector_dim, dtype = np.float32)
    
    hnsw_db.add(vec_a, {"id": "doc_a"})
    results = hnsw_db.dense_search(query_vector = vec_b, top_k = 1)
    
    assert pytest.approx(results[0]["distance"], abs = 1e-5) == 2.0, f"Lỗi: Cosine distance của 2 vector đối nghịch phải = 2.0, nhận {results[0]['distance']}."


"""Test 4: Hệ thống phải trả về chính xác số lượng top_k kết quả."""
def test_dense_top_k_retrieval(hnsw_db, vector_dim):
    
    for i in range(5):
        hnsw_db.add(np.random.rand(vector_dim).astype(np.float32), {"id": f"doc_{i}"})
    
    query = np.random.rand(vector_dim).astype(np.float32)
    results = hnsw_db.dense_search(query_vector = query, top_k=3)
    
    assert len(results) == 3, f"Lỗi: Kỳ vọng trả về 3 kết quả (top_k=3), nhưng hệ thống trả về {len(results)} kết quả."


# ==============================
# 2. Edge Cases & Constraints
# ==============================


"""Test 5: top_k lớn hơn số lượng doc trong DB thì chỉ trả về tối đa số doc hiện có."""
def test_dense_top_k_exceeds_db_size(hnsw_db, sample_vector):
    
    hnsw_db.add(sample_vector, {"id": "doc_1"})
    
    results = hnsw_db.dense_search(query_vector = sample_vector, top_k = 10)
    assert len(results) == 1, f"Lỗi: DB chỉ có 1 doc nhưng hệ thống trả về {len(results)} kết quả khi truy vấn top_k=10."


"""Test 6: Truy vấn trên DB rỗng không được crash mà phải trả về list rỗng."""
def test_dense_empty_db(hnsw_db, sample_vector):
    
    results = hnsw_db.dense_search(query_vector = sample_vector, top_k = 5)
    assert results == [], f"Lỗi: Truy vấn trên DB rỗng phải trả về list rỗng '[]', nhưng nhận được {results}."


"""Test 7: Tie-break - Nếu khoảng cách bằng nhau, phải ưu tiên stable code ID hoặc thứ tự nhất quán."""
def test_dense_tie_breaking(hnsw_db, vector_dim):
    
    same_vector = np.random.rand(vector_dim).astype(np.float32)
    hnsw_db.add(same_vector, {"id": "B_doc"}) # ID lớn hơn
    hnsw_db.add(same_vector, {"id": "A_doc"}) # ID nhỏ hơn
    
    results = hnsw_db.dense_search(query_vector=same_vector, top_k=2)
    # Kỳ vọng stable sort theo ID alphabet hoặc cơ chế tie-break của team
    assert results[0]["metadata"]["id"] == "A_doc", f"Lỗi: Cơ chế Tie-break thất bại. Không ưu tiên ID stable 'A_doc' khi khoảng cách bằng nhau, nhận ID '{results[0]['metadata']['id']}' lên đầu." 


# ==============================
# 3. Error Handling
# ==============================


"""Test 8: Truy vấn bằng vector toàn số 0 phải bị từ chối."""
def test_dense_reject_zero_query(hnsw_db, vector_dim):
    
    zero_query = np.zeros(vector_dim, dtype = np.float32)
    
    try:
        hnsw_db.dense_search(query_vector = zero_query, top_k = 1)
        pytest.fail("Lỗi: Hệ thống cho phép truy vấn Zero Vector.")
    
    except ValueError:
        pass


"""Test 9: Vector chứa NaN hoặc Infinity không thể tính toán Cosine và phải bị từ chối."""
def test_dense_reject_nan_inf_query(hnsw_db, vector_dim):
    
    invalid_query = np.random.rand(vector_dim).astype(np.float32)
    invalid_query[0] = np.nan
    
    try:
        hnsw_db.dense_search(query_vector = invalid_query, top_k = 1)
        pytest.fail("Lỗi: Hệ thống cho phép truy vấn Vector chứa giá trị NaN.")
    
    except ValueError:
        pass


"""Test 10: Vector truy vấn sai số chiều (dimension) phải bị reject."""
def test_dense_dimension_mismatch(hnsw_db, vector_dim):

    wrong_query = np.random.rand(vector_dim - 5).astype(np.float32)
    
    try:
        hnsw_db.dense_search(query_vector = wrong_query, top_k = 1)
        pytest.fail("Lỗi: Hệ thống cho phép truy vấn vector có số chiều không hợp lệ.")
    
    except ValueError:
        pass