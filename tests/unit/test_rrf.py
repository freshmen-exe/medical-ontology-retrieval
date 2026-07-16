import pytest

# Giả định import hàm từ module của dev team (cần đổi lại đường dẫn cho đúng code thực tế)
# from src.feature.reranking import compute_rrf

# ---------------------------------------------------------
# MÔ PHỎNG HÀM RRF (Chỉ dùng để code test chạy được nếu dev chưa code xong)
# ---------------------------------------------------------
def compute_rrf(dense_ranks: dict, sparse_ranks: dict, k: int = 60) -> dict:
    if k <= 0:
        raise ValueError("Hằng số k phải lớn hơn 0")
    
    rrf_scores = {}
    all_candidates = set(dense_ranks.keys()).union(set(sparse_ranks.keys()))
    
    for candidate in all_candidates:
        score = 0.0
        if candidate in dense_ranks:
            if dense_ranks[candidate] <= 0: raise ValueError("Rank phải lớn hơn 0")
            score += 1.0 / (k + dense_ranks[candidate])
        if candidate in sparse_ranks:
            if sparse_ranks[candidate] <= 0: raise ValueError("Rank phải lớn hơn 0")
            score += 1.0 / (k + sparse_ranks[candidate])
        rrf_scores[candidate] = score
        
    # Sort theo điểm số giảm dần, nếu hòa điểm (tie) thì sort theo alphabet của keys
    sorted_scores = dict(sorted(rrf_scores.items(), key=lambda item: (-item[1], item[0])))
    return sorted_scores
# ---------------------------------------------------------

class TestRRF:
    
    """
    Tập hợp các unit test kiểm thử thuật toán Reciprocal Rank Fusion (RRF).
    
    """


    # Test 1: Kiểm tra tính toán cơ bản khi cả 2 luồng đều đồng thuận ở vị trí số 1
    def test_rrf_absolute_consensus(self, dense_mock, sparse_mock, smoothing_const):
        
        result = compute_rrf(dense_mock, sparse_mock, k = smoothing_const)
        expected_score = (1 / 61) + (1 / 61)
        
        assert result["ICD-001"] == pytest.approx(expected_score, rel=1e-5), "Lỗi: Điểm RRF cho ứng viên Top 1 đồng thuận tính toán sai công thức"


    # Test 2: Kiểm tra sự thay đổi điểm số khi có sự lệch pha lớn về rank (1 và 100)
    def test_rrf_rank_disparity(self, smoothing_const):
        
        result = compute_rrf({"ICD-A": 1}, {"ICD-A": 100}, k = smoothing_const)
        expected_score = (1 / 61) + (1 / 160)
        
        assert result["ICD-A"] == pytest.approx(expected_score, rel=1e-5), "Lỗi: Thuật toán xử lý sai khi chênh lệch rank giữa Dense và Sparse quá lớn"


    # Test 3: Kiểm tra xử lý trường hợp mã y khoa chỉ xuất hiện ở Dense Search
    def test_rrf_missing_in_sparse(self, dense_mock, smoothing_const):
        
        result = compute_rrf(dense_mock, {}, k = smoothing_const)
        expected_score = 1 / 65 # Mã ICD-003 đứng top 5
        
        assert "ICD-003" in result, "Lỗi: Ứng viên bị mất tích nếu không có mặt trong Sparse Search"
        
        assert result["ICD-003"] == pytest.approx(expected_score, rel=1e-5), "Lỗi: Điểm RRF tính sai khi khuyết dữ liệu Sparse"


    # Test 4: Kiểm tra xử lý trường hợp mã y khoa chỉ xuất hiện ở Sparse Search
    def test_rrf_missing_in_dense(self, sparse_mock, smoothing_const):
        
        result = compute_rrf({}, sparse_mock, k = smoothing_const)
        expected_score = 1 / 62 # Mã ICD-004 đứng top 2
        
        assert "ICD-004" in result, "Lỗi: Ứng viên bị mất tích nếu không có mặt trong Dense Search"
        
        assert result["ICD-004"] == pytest.approx(expected_score, rel = 1e-5), "Lỗi: Điểm RRF tính sai khi khuyết dữ liệu Dense"


    # Test 5: Kiểm tra cơ chế phân giải hòa điểm (Tie-breaking) sắp xếp theo Alphabet nếu điểm bằng nhau
    def test_rrf_tie_breaker(self, smoothing_const):
        
        # ICD-A và ICD-B có rank hoán đổi nhau, tổng điểm RRF sẽ bằng nhau tuyệt đối
        result = compute_rrf({"ICD-B": 2, "ICD-A": 5}, {"ICD-B": 5, "ICD-A": 2}, k = smoothing_const)
        top_candidates = list(result.keys())
        
        assert top_candidates[0] == "ICD-A" and top_candidates[1] == "ICD-B", "Lỗi: Cơ chế Tie-breaker không sắp xếp ổn định theo mã ICD khi hòa điểm"


    # Test 6: Kiểm tra tác động của hằng số k (Smoothing constant)
    def test_rrf_custom_k_constant(self, smoothing_const):
    
        result_k60 = compute_rrf({"ICD-A": 1}, {"ICD-A": 1}, k = smoothing_const)
        result_k1 = compute_rrf({"ICD-A": 1}, {"ICD-A": 1}, k = 1)
    
        assert result_k60["ICD-A"] < result_k1["ICD-A"], "Lỗi: Hằng số K không có tác dụng làm mượt/giảm sự chênh lệch điểm số"


    # Test 7: Kiểm tra độ bền vững (Robustness) khi cả 2 đầu vào đều rỗng
    def test_rrf_empty_inputs(self, smoothing_const):
        
        result = compute_rrf({}, {}, k = smoothing_const)
        
        assert isinstance(result, dict) and len(result) == 0, "Lỗi: Hàm không trả về dictionary rỗng khi 2 luồng Search không tìm thấy kết quả nào"


    # Test 8: Kiểm tra thứ tự sắp xếp trả về (Sorting validation)
    def test_rrf_output_sorting(self, dense_mock, sparse_mock, smoothing_const):
        
        result = compute_rrf(dense_mock, sparse_mock, k = smoothing_const)
        scores = list(result.values())
        
        assert all(scores[i] >= scores[i+1] for i in range(len(scores)-1)), "Lỗi: Dictionary đầu ra không được sắp xếp theo điểm RRF giảm dần"


    # Test 9: Kiểm tra bắt lỗi nếu Dev truyền rank không hợp lệ (Rank <= 0)
    def test_rrf_invalid_rank_error(self, smoothing_const):
        
        try:
            compute_rrf({"ICD-ERR": 0}, {}, k = smoothing_const)
            pytest.fail("Lỗi nghiêm trọng: Hàm không bắt lỗi khi Rank = 0 (Thứ hạng phải bắt đầu từ 1)")
        
        except ValueError:
            pass # Đúng như kỳ vọng


    # Test 10: Kiểm tra bắt lỗi nếu Dev truyền hằng số k <= 0
    def test_rrf_invalid_k_constant_error(self):
        try:
            compute_rrf({"ICD-A": 1}, {"ICD-A": 2}, k = 0)
            pytest.fail("Lỗi nghiêm trọng: Hàm không bắt lỗi khi truyền hằng số k <= 0")
        except ValueError:
            pass # Đúng như kỳ vọng