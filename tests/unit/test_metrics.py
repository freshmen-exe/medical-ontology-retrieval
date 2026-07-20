import pytest
# Giả định module chứa các hàm tính toán là src.evaluation.metrics
# from src.evaluation.metrics import calculate_wer, calculate_jaccard, calculate_candidate_score, calculate_final_score, evaluate_concept


class TestLocalScorer:


    # Test 1: Kiểm thử hàm tính Word Error Rate (WER) cho trường text với text đúng hoàn toàn và text thiếu từ.
    def test_wer_text_score(self):

        gold_text = "bệnh trào ngược dạ dày thực quản"
        predicted_perfect_text = "bệnh trào ngược dạ dày thực quản"  
        predicted_partial_text = "trào ngược dạ dày"                    
        
        score_perfect = calculate_wer(gold_text, predicted_perfect_text)
        score_partial = calculate_wer(gold_text, predicted_partial_text)
        
        assert score_perfect == 1.0, f"Lỗi WER: Text giống hệt nhau phải đạt điểm 1.0, nhưng nhận được {score_perfect}"

        assert 0.0 < score_partial < 1.0, f"Lỗi WER: Text dự đoán thiếu từ phải bị trừ điểm, nhưng nhận được {score_partial}"


    # Test 2: Kiểm thử hàm tính độ tương đồng Jaccard cho assertions trong các kịch bản: trùng khớp, rỗng, đoán thừa, trùng 1 phần.
    def test_jaccard_assertions(self):

        # Case 1: Trùng khớp hoàn toàn (Perfect Match)
        gold_historical_and_family = ["isHistorical", "isFamily"]
        predicted_historical_and_family = ["isHistorical", "isFamily"]

        score_perfect_match = calculate_jaccard(gold_historical_and_family, predicted_historical_and_family)

        assert score_perfect_match == 1.0, "Lỗi Jaccard (Trùng khớp): Hai mảng assertions giống nhau phải đạt 1.0"

        # Case 2: Rỗng hoàn toàn (Edge case)
        gold_no_assertions = []
        predicted_no_assertions = []

        score_both_empty = calculate_jaccard(gold_no_assertions, predicted_no_assertions)

        assert score_both_empty == 1.0, "Lỗi Jaccard (Cả hai rỗng): Theo luật BTC, hai tập rỗng phải tính Jaccard = 1.0"

        # Case 3: Dự đoán thừa
        gold_empty_assertions = []
        predicted_extra_negated = ["isNegated"]

        score_over_prediction = calculate_jaccard(gold_empty_assertions, predicted_extra_negated)

        assert score_over_prediction == 0.0, "Lỗi Jaccard (Dự đoán thừa): Nhãn gốc rỗng nhưng đoán thừa cờ phải đạt 0.0"

        # Case 4: Trùng một phần
        gold_historical_only = ["isHistorical"]
        predicted_historical_with_negated = ["isHistorical", "isNegated"]

        score_partial_match = calculate_jaccard(gold_historical_only, predicted_historical_with_negated)

        assert score_partial_match == 0.5, "Lỗi Jaccard (Trùng 1 phần): Giao 1, hợp 2 thì Jaccard phải là 0.5"


    # Test 3: Kiểm thử hàm tính Jaccard có trọng số cho candidates (Đoán trúng 100% ICD code và đoán trúng 1 phần).
    def test_weighted_jaccard_candidates(self):
        gold_candidates = ["K21.0", "K21.9"]
        predicted_perfect_candidates = ["K21.0", "K21.9"]
        predicted_partial_candidates = ["K21.0"]
        
        score_perfect = calculate_candidate_score(gold_candidates, predicted_perfect_candidates)
        score_partial = calculate_candidate_score(gold_candidates, predicted_partial_candidates)
        
        assert score_perfect == 1.0, "Lỗi Candidate: Đoán đúng toàn bộ danh sách ICD phải đạt 1.0 điểm"

        assert score_partial == 0.5, "Lỗi Candidate: Đoán trúng 1/2 mã ICD thì Jaccard phải là 0.5"


    # Test 4: Kiểm thử Edge Case trừng phạt cốt lõi: Gán 0 điểm cho toàn bộ metrics nếu đoán sai nhãn Type y khoa.
    def test_edge_case_wrong_type_punishment(self, sample_metadata):
        ground_truth = sample_metadata.copy()
        
        prediction = sample_metadata.copy()
        prediction["type"] = "TRIỆU_CHỨNG"  # Nhãn gốc trong fixture là "CHẨN_ĐOÁN"
        
        scores = evaluate_concept(ground_truth, prediction)
        
        assert scores["text_score"] == 0.0, "Lỗi Penalty: Đoán sai Type, text_score phải bị gán 0.0"

        assert scores["assertions_score"] == 0.0, "Lỗi Penalty: Đoán sai Type, assertions_score phải bị gán 0.0"

        assert scores["candidates_score"] == 0.0, "Lỗi Penalty: Đoán sai Type, candidates_score phải bị gán 0.0"


    # Test 5: Kiểm tra việc tổng hợp điểm số cuối cùng bám sát tỷ lệ trọng số của BTC (0.3 * Text + 0.3 * Assertions + 0.4 * Candidates).
    def test_final_score_aggregation(self):
        avg_text_score = 0.8
        avg_assertions_score = 0.9
        avg_candidates_score = 0.7
        
        expected_final = (0.3 * avg_text_score) + (0.3 * avg_assertions_score) + (0.4 * avg_candidates_score)
        actual_final = calculate_final_score(avg_text_score, avg_assertions_score, avg_candidates_score)
        
        assert actual_final == pytest.approx(expected_final, rel=1e-5), \
            f"Lỗi Aggregate: Hàm tổng hợp điểm sai công thức BTC. Cần {expected_final} nhưng nhận {actual_final}"


    # Test 6: Kiểm thử mức sàn (Cận dưới 0.0) của WER khi text dự đoán hoàn toàn sai lệch hoặc bỏ trống (để chặn điểm âm).
    def test_wer_completely_wrong_or_empty(self):
        gold_text = "ung thư phổi"
        predicted_wrong_text = "đau dạ dày"
        predicted_empty_text = ""
        
        score_wrong = calculate_wer(gold_text, predicted_wrong_text)
        score_empty = calculate_wer(gold_text, predicted_empty_text)
        
        assert score_wrong == 0.0, f"Lỗi WER: Text khác hoàn toàn phải bị 0.0 điểm, nhưng nhận được {score_wrong}"

        assert score_empty == 0.0, f"Lỗi WER: Text rỗng phải bị 0.0 điểm, nhưng nhận được {score_empty}"


    # Test 7: Kiểm thử mức sàn (Cận dưới 0.0) của Candidate Score khi mảng dự đoán không chứa mã ICD nào trùng với nhãn chuẩn.
    def test_candidates_no_overlap(self):
        gold_icd_codes = ["C34.9"]
        predicted_icd_codes = ["K21.0", "J01.9"]
        
        score_no_overlap = calculate_candidate_score(gold_icd_codes, predicted_icd_codes)
        
        assert score_no_overlap == 0.0, (
            f"Lỗi Candidate: Không trúng mã ICD nào phải đạt 0.0 điểm, "
            f"nhưng nhận được {score_no_overlap}"
        )


    # Test 8: Kiểm thử hàm Evaluate Concept tổng quát trả về điểm tuyệt đối (1.0) cho mọi keys khi dự đoán hoàn hảo.
    def test_evaluate_concept_perfect_match(self, sample_metadata):
        ground_truth = sample_metadata.copy()
        prediction = sample_metadata.copy()
        
        scores = evaluate_concept(ground_truth, prediction)
        
        assert scores["text_score"] == 1.0, "Lỗi Evaluate: Text hoàn hảo phải trả về 1.0"

        assert scores["assertions_score"] == 1.0, "Lỗi Evaluate: Assertions hoàn hảo phải trả về 1.0"

        assert scores["candidates_score"] == 1.0, "Lỗi Evaluate: Candidates hoàn hảo phải trả về 1.0"

        assert scores["final_score"] == 1.0, "Lỗi Evaluate: Final Score hoàn hảo phải trả về 1.0"


    # Test 9: Kiểm thử tính chống chịu (Robustness) của Scorer khi JSON/Dict dự đoán bị thiếu hụt hẳn trường thông tin phụ.
    def test_evaluate_concept_missing_optional_keys(self, sample_metadata):
        ground_truth = sample_metadata.copy()
        
        # Cố tình thiếu key "assertions" và "candidates"
        prediction = {
            "text": ground_truth["text"],
            "type": ground_truth["type"]
        }
        
        # Hàm tính toán phải tự fallback các keys thiếu thành mảng rỗng [] thay vì crash KeyError
        scores = evaluate_concept(ground_truth, prediction)
        
        # Vì nhãn gốc có cờ và ICD, nhưng dự đoán trống -> Jaccard = 0.0
        assert scores["assertions_score"] == 0.0, "Lỗi Robustness: Scorer không xử lý được việc thiếu key 'assertions'"
        
        assert scores["candidates_score"] == 0.0, "Lỗi Robustness: Scorer không xử lý được việc thiếu key 'candidates'"
        
        assert scores["text_score"] == 1.0, "Lỗi Robustness: Text score vẫn phải đạt 1.0 bất chấp thiếu keys khác"


    # Test 10: Kiểm thử Edge Case cho Candidate Jaccard khi cả nhãn gốc lẫn dự đoán đều không có bất kỳ mã ICD nào.
    def test_candidates_both_empty(self):
        gold_empty_icd = []
        predicted_empty_icd = []
        
        score_empty_match = calculate_candidate_score(gold_empty_icd, predicted_empty_icd)
        
        assert score_empty_match == 1.0, (
            f"Lỗi Candidate: Cả 2 danh sách ICD đều rỗng thì Jaccard theo luật phải gán là 1.0, "
            f"nhưng nhận được {score_empty_match}"
        )