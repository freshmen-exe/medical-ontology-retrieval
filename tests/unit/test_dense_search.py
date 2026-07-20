import pytest
import numpy as np


class TestDenseSearch:
    """
    Bộ kiểm thử cho chức năng Dense Search (tìm kiếm bằng Cosine Distance)
    của HNSW Vectorbase. Đã tinh chỉnh tương thích với Numba Float16 Core.
    """

    # ==============================
    # 1. Normal Dense Search Operations
    # ==============================

    """Test 1: Truy vấn exact match trả về khoảng cách Cosine bằng 0"""
    def test_dense_exact_match(self, hnsw_db, sample_vector):
        
        hnsw_db.add(sample_vector, {"id": "doc_1"})
        results = hnsw_db.dense_search(query_vector=sample_vector, top_k=1)
        
        assert len(results) > 0, "Lỗi: Truy vấn exact match không trả về kết quả nào."
        
        assert results[0]["metadata"]["id"] == "doc_1", f"Lỗi: Sai ID kết quả. Kỳ vọng 'doc_1', nhận '{results[0]['metadata']['id']}'."
        
        # Nới lỏng dung sai xuống 1e-3 do core lưu trữ bằng float16
        assert pytest.approx(results[0]["distance"], abs=1e-3) == 0.0, f"Lỗi: Cosine distance phải ~0.0, nhận {results[0]['distance']}."


    """Test 2: Hai vector vuông góc có khoảng cách Cosine bằng 1.0 """
    def test_dense_orthogonal_vectors(self, hnsw_db, vector_dim):
        
        vec_a = np.zeros(vector_dim, dtype=np.float32)
        vec_a[0] = 1.0  
        vec_b = np.zeros(vector_dim, dtype=np.float32)
        vec_b[1] = 1.0  
        
        hnsw_db.add(vec_a, {"id": "doc_a"})
        results = hnsw_db.dense_search(query_vector = vec_b, top_k = 1)
        
        assert pytest.approx(results[0]["distance"], abs=1e-3) == 1.0, f"Lỗi: Cosine distance vuông góc phải ~1.0, nhận {results[0]['distance']}."


    """Test 3: Hai vector đối nghịch có khoảng cách Cosine bằng 2.0 """
    def test_dense_opposite_vectors(self, hnsw_db, vector_dim):

        vec_a = np.ones(vector_dim, dtype=np.float32)
        vec_b = -np.ones(vector_dim, dtype=np.float32)
        
        hnsw_db.add(vec_a, {"id": "doc_a"})
        results = hnsw_db.dense_search(query_vector = vec_b, top_k = 1)
        
        assert pytest.approx(results[0]["distance"], abs=1e-3) == 2.0, f"Lỗi: Cosine distance đối nghịch phải ~2.0, nhận {results[0]['distance']}."


    """Test 4: Hệ thống phải trả về chính xác số lượng top_k kết quả từ DB có sẵn."""
    def test_dense_top_k_retrieval(self, populated_db, vector_dim):
        
        # Sử dụng trực tiếp populated_db từ conftest (đã có sẵn 10 mock vectors)
        query = np.random.rand(vector_dim).astype(np.float32)
        results = populated_db.dense_search(query_vector=query, top_k = 3)
        
        assert len(results) == 3, f"Lỗi: Kỳ vọng trả về 3 kết quả (top_k=3), nhưng hệ thống trả về {len(results)} kết quả."


    # ==============================
    # 2. Edge Cases & Constraints
    # ==============================

    """Test 5: top_k lớn hơn số lượng doc trong DB thì chỉ trả về tối đa số doc hiện có."""
    def test_dense_top_k_exceeds_db_size(self, hnsw_db, sample_vector):
        
        hnsw_db.add(sample_vector, {"id": "doc_1"})
        results = hnsw_db.dense_search(query_vector=sample_vector, top_k=10)
        
        assert len(results) == 1, f"Lỗi: DB chỉ có 1 doc nhưng hệ thống trả về {len(results)} kết quả khi truy vấn top_k=10."


    """Test 6: Truy vấn trên DB rỗng không được crash (tránh lỗi RuntimeError của core)."""
    def test_dense_empty_db(self, hnsw_db, sample_vector):
        
        results = hnsw_db.dense_search(query_vector=sample_vector, top_k=5)
        assert results == [], f"Lỗi: Truy vấn trên DB rỗng phải trả về list rỗng '[]', nhận được {results}."


    """Test 7: Tie-break - Khoảng cách bằng nhau phải trả về 2 kết quả không bị lọt ID."""
    def test_dense_tie_breaking(self, hnsw_db, vector_dim):
        
        same_vector = np.random.rand(vector_dim).astype(np.float32)
        hnsw_db.add(same_vector, {"id": "B_doc"}) 
        hnsw_db.add(same_vector, {"id": "A_doc"}) 
        
        results = hnsw_db.dense_search(query_vector=same_vector, top_k=2)
        returned_ids = [res["metadata"]["id"] for res in results]
        
        assert "A_doc" in returned_ids and "B_doc" in returned_ids, "Lỗi: Hệ thống làm mất mát (drop) kết quả khi các vector có khoảng cách giống hệt nhau."


    # ==============================
    # 3. Error Handling
    # ==============================

    """Test 8: Truy vấn bằng vector toàn số 0 (Zero Vector) phải bị từ chối."""
    def test_dense_reject_zero_query(self, hnsw_db, vector_dim):
        
        zero_query = np.zeros(vector_dim, dtype=np.float32)
        
        try:
            hnsw_db.dense_search(query_vector=zero_query, top_k=1)
            pytest.fail("Lỗi: Hệ thống cho phép truy vấn Zero Vector (Gây lỗi chia cho 0 khi tính Cosine).")
        except ValueError:
            pass


    """Test 9: Vector chứa NaN không thể tính toán khoảng cách và phải bị từ chối."""
    def test_dense_reject_nan_inf_query(self, hnsw_db, vector_dim):
        
        invalid_query = np.random.rand(vector_dim).astype(np.float32)
        invalid_query[0] = np.nan
        
        try:
            hnsw_db.dense_search(query_vector=invalid_query, top_k=1)
            pytest.fail("Lỗi: Hệ thống cho phép truy vấn Vector chứa giá trị NaN/Infinity.")
        except ValueError:
            pass


    """Test 10: Vector truy vấn sai số chiều (dimension mismatch) phải bị reject."""
    def test_dense_dimension_mismatch(self, hnsw_db, vector_dim):
        # Đã fix lỗi logic: Cộng thêm chiều thay vì trừ để tránh lỗi mảng âm của Numpy
        wrong_query = np.random.rand(vector_dim + 5).astype(np.float32)
        
        try:
            hnsw_db.dense_search(query_vector=wrong_query, top_k=1)
            pytest.fail("Lỗi: Hệ thống cho phép truy vấn vector có số chiều không khớp với DB (Dimension Mismatch).")
        except ValueError:
            pass