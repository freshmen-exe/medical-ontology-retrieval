import pytest

# Giả lập import hàm từ src
from src.candidate_ranker import rank_candidates

class TestCandidateRanker:

    # Test 1: Kiểm tra loại bỏ triệt để các candidate có điểm số nhỏ hơn ngưỡng threshold cho trước.
    
    def test_1_threshold_filtering(self):
        
        raw_candidates = [
            {"id": "K21.0", "score": 0.8}, # Bệnh trào ngược dạ dày thực quản (Hợp lệ)
            {"id": "K21.9", "score": 0.3}, # Dưới ngưỡng 0.5
            {"id": "E11.9", "score": 0.1}  # Dưới ngưỡng 0.5
        ]
        result = rank_candidates(raw_candidates, entity_type="CHẨN_ĐOÁN", threshold=0.5)
        
        assert result == ["K21.0"], f"Lỗi: Ranker không lọc đúng threshold. Nhận được {result}"


    # Test 2: Kiểm tra chức năng cắt đúng Top K (Top 5) khi số lượng candidate vượt quá giới hạn.
    def test_2_top_k_capping(self):
        
        # Dùng format mã RxNorm giả lập cho THUỐC
        raw_candidates = [{"id": f"1980{i}", "score": 1.0 - (i * 0.1)} for i in range(10)]
        result = rank_candidates(raw_candidates, entity_type="THUỐC", top_k=5)
        
        assert len(result) == 5, f"Lỗi: Ranker không cắt đúng Top 5. Nhận được {len(result)} phần tử."
        
        assert result == ["19800", "19801", "19802", "19803", "19804"], "Lỗi: Sai thứ tự hoặc sai ID."


    # Test 3: Kiểm tra cơ chế hòa điểm (Tie-breaking) ưu tiên mã code theo thứ tự alphabet khi điểm bằng nhau.
    def test_3_tie_breaking_alphabetical(self):
        
        raw_candidates = [
            {"id": "Z00.0", "score": 0.5},
            {"id": "A00.0", "score": 0.5},
            {"id": "M00.0", "score": 0.5}
        ]
        result = rank_candidates(raw_candidates, entity_type="CHẨN_ĐOÁN")
        expected_order = ["A00.0", "M00.0", "Z00.0"]
        
        assert result == expected_order, f"Lỗi Tie-breaking: Kỳ vọng {expected_order}, nhận được {result}"


    # Test 4: Kiểm tra tính hợp lệ khi entity type là CHẨN_ĐOÁN hoặc THUỐC thì được phép trả về candidates.
    @pytest.mark.parametrize("valid_type", ["CHẨN_ĐOÁN", "THUỐC"])
    def test_4_valid_entity_types_allowed(self, valid_type):
        
        raw_candidates = [{"id": "A09", "score": 0.9}]
        result = rank_candidates(raw_candidates, entity_type=valid_type)
        
        assert result == ["A09"], f"Lỗi: Entity type '{valid_type}' hợp lệ nhưng Ranker trả về rỗng."


    # Test 5: Không được trả về candidates đối với các nhãn TRIỆU_CHỨNG, TÊN_XÉT_NGHIỆM, KẾT_QUẢ_XÉT_NGHIỆM.
    @pytest.mark.parametrize("invalid_type", ["TRIỆU_CHỨNG", "TÊN_XÉT_NGHIỆM", "KẾT_QUẢ_XÉT_NGHIỆM"])
    
    def test_5_invalid_entity_types_blocked(self, invalid_type):
        
        raw_candidates = [{"id": "R05", "score": 0.9}] # R05: Ho (Triệu chứng)
        result = rank_candidates(raw_candidates, entity_type=invalid_type)
        
        assert result == [], f"Lỗi nghiêm trọng: Không được gán candidate cho '{invalid_type}'."


    # Test 6: Kiểm tra độ bền (Robustness) của hàm khi đầu vào là một mảng rỗng.
    def test_6_empty_input_handling(self):
        
        result = rank_candidates([], entity_type="CHẨN_ĐOÁN")
        
        assert result == [], f"Lỗi: Đầu vào rỗng phải trả về []. Nhận được {result}"


    # Test 7: Kiểm tra trường hợp danh sách ứng viên có số lượng bằng đúng Top K quy định.
    def test_7_exact_top_k_input(self):
        
        raw_candidates = [{"id": f"A0{i}", "score": 0.8} for i in range(5)]
        
        result = rank_candidates(raw_candidates, entity_type="CHẨN_ĐOÁN", top_k=5)
        
        assert len(result) == 5, "Lỗi: Không trả về đủ 5 phần tử khi đầu vào có đúng 5 phần tử."


    # Test 8: Kiểm tra trường hợp toàn bộ candidate đều có điểm thấp hơn ngưỡng threshold.
    def test_8_all_below_threshold(self):
        
        raw_candidates = [{"id": "A01", "score": 0.1}, {"id": "A02", "score": 0.2}]
        
        result = rank_candidates(raw_candidates, entity_type="CHẨN_ĐOÁN", threshold=0.5)
        
        assert result == [], "Lỗi: Toàn bộ dưới ngưỡng nhưng vẫn lọt candidate."


    # Test 9: Xác minh danh sách ID đầu ra luôn được sắp xếp theo thứ tự điểm số giảm dần.
    def test_9_score_sorting_order(self):
        
        raw_candidates = [
            {"id": "LOW_CODE", "score": 0.2},
            {"id": "HIGH_CODE", "score": 0.9},
            {"id": "MED_CODE", "score": 0.5}
        ]
        result = rank_candidates(raw_candidates, entity_type="THUỐC")
        
        assert result == ["HIGH_CODE", "MED_CODE", "LOW_CODE"], "Lỗi Sorting: Không sắp xếp giảm dần theo score."


    # Test 10: Xử lý an toàn khi dictionary candidate bị khuyết thiếu key 'score' từ các chặng trước.
    def test_10_missing_score_key_handling(self):
        
        # Kiểm tra sự bền bỉ của code thực thi, không dùng try-except ở level bài test
        malformed_candidates = [{"id": "A00"}, {"id": "B00", "score": 0.8}]
        
        # Test nên pass nếu Dev code an toàn (ví dụ dùng .get('score', 0)). 
        # Nếu hàm bị lỗi KeyError, Pytest sẽ tự Fail và show Traceback cho Dev sửa.
        result = rank_candidates(malformed_candidates, entity_type="CHẨN_ĐOÁN")
        
        assert "B00" in result, "Lỗi: Ranker không nhận diện được data đúng khi có data khuyết key."