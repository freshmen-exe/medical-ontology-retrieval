import pytest

# ==============================
# 1. Normal Sparse Search Operations
# ==============================


"""Test 1: Truy vấn từ khóa trùng khớp 100% phải trả về kết quả."""
def test_sparse_exact_keyword_match(bm25_db):
    
    bm25_db.add_document("doc_1", "bệnh nhân trào ngược dạ dày")
    
    results = bm25_db.sparse_search(query_text = "dạ dày", top_k = 1)
    
    assert len(results) > 0, "Truy vấn từ khóa trùng khớp 100% nhưng hệ thống trả về danh sách rỗng."
    assert results[0]["id"] == "doc_1", f"Lỗi exact-keyword : Kỳ vọng kết quả top 1 là 'doc_1', nhưng nhận được '{results[0]['id']}'."


"""Test 2: Document có tần suất xuất hiện (TF) từ khóa cao hơn phải có điểm cao hơn."""
def test_sparse_term_frequency_effect(bm25_db):
    
    bm25_db.add_document("doc_1", "ho khan")
    bm25_db.add_document("doc_2", "ho đờm, ho dai dẳng, ho kéo dài") # "ho" xuất hiện 3 lần
    
    results = bm25_db.sparse_search(query_text = "ho", top_k = 2)
    
    assert results[0]["id"] == "doc_2", "Lỗi TF: Tài liệu có tần suất xuất hiện từ khóa cao hơn không được xếp hạng top 1."


"""Test 3: Document ngắn hơn (chứa keyword) phải có điểm cao hơn Document dài (chứa keyword) do hệ số b."""
def test_sparse_document_length_effect(bm25_db):
    
    bm25_db.add_document("doc_short", "viêm phổi")
    bm25_db.add_document("doc_long", "bệnh nhân có tiền sử viêm phổi từ năm ngoái và hiện tại đang bình thường")
    
    results = bm25_db.sparse_search(query_text = "viêm phổi", top_k = 2)
    
    assert results[0]["id"] == "doc_short", "Lỗi phạt độ dài: Tài liệu chứa keyword nhưng ngắn hơn không được ưu tiên xếp hạng cao hơn tài liệu dài."


"""Test 4: IDF (Inverse Document Frequency) - Từ hiếm phải đóng góp điểm số cao hơn từ phổ biến."""
def test_sparse_idf_rarity_effect(bm25_db):
    
    bm25_db.add_document("doc_1", "bệnh nhân bị sốt")
    bm25_db.add_document("doc_2", "bệnh nhân bị paracetamol") # giả sử paracetamol là từ hiếm
    bm25_db.add_document("doc_3", "bệnh nhân khỏe")
    
    # "bệnh nhân" có trong cả 3 doc, "paracetamol" chỉ có trong 1 doc.
    # Truy vấn cả cụm, doc_2 phải thắng doc_1 và doc_3.
    results = bm25_db.sparse_search(query_text = "bệnh nhân paracetamol", top_k = 1)
    
    assert results[0]["id"] == "doc_2", "Lỗi IDF: Từ hiếm ('paracetamol') không chiếm trọng số cao hơn từ phổ biến ('bệnh nhân')."

# ==============================
# 2. Edge Cases & Filters
# ==============================


"""Test 5: Truy vấn Out-Of-Vocabulary (từ không có trong index) phải trả về điểm 0 hoặc rỗng."""
def test_sparse_oov_query(bm25_db):
    
    bm25_db.add_document("doc_1", "đau bụng")
    results = bm25_db.sparse_search(query_text = "đau đầu", top_k = 1)
    
    # Tùy thiết kế, có thể list rỗng hoặc score = 0
    assert len(results) == 0 or results[0]["score"] == 0.0, "Lỗi OOV: Truy vấn từ không tồn tại trong index nhưng không bị loại trừ hoặc vẫn có điểm lớn hơn 0."


"""Test 6: BM25 thường phải có tokenizer xử lý case-insensitive (không phân biệt hoa/thường)."""
def test_sparse_case_and_diacritic_insensitivity(bm25_db):
    
    bm25_db.add_document("doc_1", "Viêm Gan B")
    
    results = bm25_db.sparse_search(query_text = "viêm gan b", top_k = 1)
    
    assert len(results) == 1, "Lỗi Tokenizer: Hệ thống BM25 không xử lý được case-insensitive, không match được chữ hoa với chữ thường."


"""Test 7: Cách xử lý từ trùng lặp trong câu query không được làm crash hệ thống."""
def test_sparse_duplicate_query_terms(bm25_db):
    
    bm25_db.add_document("doc_1", "đau ngực")
    
    # Query lặp lại từ "đau" nhiều lần
    results = bm25_db.sparse_search(query_text = "đau đau đau ngực", top_k = 1)
    
    assert len(results) == 1, "Lỗi Query: Truy vấn có từ khóa lặp lại gây lỗi hoặc trả về rỗng thay vì tìm được tài liệu hợp lệ."


"""
Test 8: Truy vấn lấy top_k nhiều hơn số lượng tài liệu chứa từ khóa 
thì chỉ trả về các tài liệu ấy thay vì ép buộc trả về đủ top_k tài liệu

"""
def test_sparse_top_k_bounds(bm25_db):
    
    bm25_db.add_document("doc_1", "sốt cao")
    bm25_db.add_document("doc_2", "đau bụng")
    
    # Chỉ doc_1 khớp "sốt", dù xin top_k=5 thì kết quả trả về chỉ nên có 1 (do doc_2 score = 0)
    results = bm25_db.sparse_search(query_text = "sốt", top_k = 5)
    
    assert len([r for r in results if r["score"] > 0]) == 1, "Lỗi Top-K/Filter: Hệ thống trả về thêm tài liệu không hợp lệ (điểm BM25 = 0) vào kết quả thay vì tự động lọc bỏ."

# ==============================
# 3. Error Handling
# ==============================


"""Test 9: Truy vấn bằng chuỗi rỗng phải bị reject hoặc trả về an toàn."""
def test_sparse_empty_query(bm25_db):
    
    bm25_db.add_document("doc_1", "khám bệnh")
    
    try:
        results = bm25_db.sparse_search(query_text = "", top_k = 1)
        assert len(results) == 0, "Lỗi Validation: Truy vấn bằng chuỗi rỗng không bị chặn mà vẫn trả về kết quả."
        
    except ValueError:
        pass # Nếu team quyết định raise error cho chuỗi rỗng thì vẫn pass
    
    except Exception as e:
        pytest.fail(f"Lỗi Logic: Khi truyền chuỗi rỗng, kỳ vọng trả về list rỗng hoặc ValueError, nhưng lại crash bằng lỗi: {type(e).__name__}")


"""Test 10: Truy vấn khi corpus của BM25 hoàn toàn trống thì vẫn hoạt động (trả về list rỗng) và không bị crash"""
def test_sparse_empty_db(bm25_db):
    
    results = bm25_db.sparse_search(query_text="sốt", top_k=5)
    assert results == [], f"Lỗi Empty DB: Khi chưa nạp dữ liệu, kỳ vọng trả về list rỗng '[]' để bảo vệ pipeline, nhưng nhận được: '{results}'"