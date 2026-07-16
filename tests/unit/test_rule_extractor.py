import pytest

# Giả lập Class Dev sẽ viết. Khi tích hợp, hãy import RuleExtractor thật từ module của team.
class MockRuleExtractor:
    
    def extract(self, text: str) -> list[dict]:
        return []

class TestRuleExtractor:
    
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Khởi tạo đối tượng Extractor trước mỗi hàm test để đảm bảo tính cô lập."""
        self.extractor = MockRuleExtractor()


    # Test 1: Trích xuất chính xác nhóm THUỐC bao gồm cả thành phần, hàm lượng, đơn vị.
    def test_1_extract_thuoc_attributes(self):
        
        raw_text = "bệnh nhân uống amlodipine 10 mg po daily"
        
        try:
            results = self.extractor.extract(raw_text)
            
            thuoc_entities = [res for res in results if res.get("type") == "THUỐC"]
            
            assert len(thuoc_entities) > 0, "Lỗi: Không trích xuất được thực thể THUỐC nào từ chuỗi chứa 'amlodipine 10 mg'."
            
            assert any(e.get("text") == "amlodipine 10 mg po daily" for e in thuoc_entities), "Lỗi: Regex trích xuất THUỐC bị cắt vụn, không bắt được đầy đủ 'tên + hàm lượng + đơn vị + liều dùng'."
        
        except AssertionError as e:
            pytest.fail(str(e))
        
        except Exception as e:
            pytest.fail(f"Lỗi hệ thống không lường trước khi test Regex THUỐC: {str(e)}")


    # Test 2: Tách biệt TÊN_XÉT_NGHIỆM và KẾT_QUẢ_XÉT_NGHIỆM theo đúng contract BTC.
    def test_2_extract_xet_nghiem_and_result(self):
        
        raw_text = "tổng phân tích tế bào máu bằng máy lazer (tbm): WBC:14,43"
        
        try:
            results = self.extractor.extract(raw_text)
            
            ten_xn = [res for res in results if res.get("type") == "TÊN_XÉT_NGHIỆM"]
            kq_xn = [res for res in results if res.get("type") == "KẾT_QUẢ_XÉT_NGHIỆM"]
            
            assert len(ten_xn) > 0, "Lỗi: Regex không bắt được TÊN_XÉT_NGHIỆM ('WBC')."
        
            assert len(kq_xn) > 0, "Lỗi: Regex không bắt được KẾT_QUẢ_XÉT_NGHIỆM ('14,43')."
            
            assert ten_xn[0].get("text") != kq_xn[0].get("text"), "Lỗi: Rule đang gộp chung tên và kết quả xét nghiệm vào một entity. BTC yêu cầu tách riêng."
        
        except AssertionError as e:
            pytest.fail(str(e))
        
        except Exception as e:
            pytest.fail(f"Lỗi hệ thống khi test XÉT_NGHIỆM: {str(e)}")


    # Test 3: Ưu tiên bắt chuỗi dài nhất (Longest match) thay vì các cụm từ ngắn.
    def test_3_longest_match_rule(self):

        raw_text = "bệnh trào ngược dạ dày - thực quản"

        try:
            results = self.extractor.extract(raw_text)
            
            chan_doan = [res for res in results if res.get("type") == "CHẨN_ĐOÁN"]
            
            assert len(chan_doan) == 1, "Lỗi: Trích xuất dư thừa, thay vì 1 cụm dài lại bị vỡ thành nhiều cụm."

            assert chan_doan[0].get("text") == "bệnh trào ngược dạ dày - thực quản", "Lỗi: Vi phạm Longest Match. Hệ thống bắt chuỗi ngắn (VD: chỉ bắt 'dạ dày') thay vì toàn bộ bệnh danh."

        except AssertionError as e:
            pytest.fail(str(e))


    # Test 4: Vẫn giữ lại Nested candidate nếu thành phần bên trong có ý nghĩa lâm sàng riêng biệt.
    def test_4_nested_candidates_retention(self):

        raw_text = "bệnh nhân dùng Panadol (Paracetamol 500mg)"

        try:
            results = self.extractor.extract(raw_text)
            
            thuoc_texts = [res.get("text") for res in results if res.get("type") == "THUỐC"]
            
            assert "Panadol" in str(thuoc_texts) and "Paracetamol 500mg" in str(thuoc_texts), "Lỗi: Longest match đang xóa sổ các hoạt chất (ingredient) lồng ghép bên trong biệt dược (brand name). Phải giữ lại cả hai."

        except AssertionError as e:
            pytest.fail(str(e))


    # Test 5: Bắt cờ isNegated từ các Rule cues cơ bản (không, chưa, âm tính).
    def test_5_assertion_is_negated(self):
        
        raw_text = "bệnh nhân không ho, chưa sốt"
        
        try:
            results = self.extractor.extract(raw_text)
            
            for res in results:
                if res.get("type") == "TRIỆU_CHỨNG":
                    assert "isNegated" in res.get("assertions", []), f"Lỗi: Bỏ sót cờ 'isNegated' cho triệu chứng bị phủ định ({res.get('text')}). Cần kiểm tra lại bộ Regex NegEx."
        
        except AssertionError as e:
            pytest.fail(str(e))


    # Test 6: Bắt cờ isHistorical từ các Rule cues cơ bản (tiền sử, đã từng).
    def test_6_assertion_is_historical(self):

        raw_text = "Bệnh nhân có tiền sử hen suyễn"

        try:
            results = self.extractor.extract(raw_text)
            
            chan_doan = next((res for res in results if res.get("type") == "CHẨN_ĐOÁN"), None)
            
            assert chan_doan is not None, "Lỗi: Không trích xuất được chẩn đoán 'hen suyễn'."

            assert "isHistorical" in chan_doan.get("assertions", []), "Lỗi: Không gán được cờ 'isHistorical' dù có trigger word 'tiền sử'."

        except AssertionError as e:
            pytest.fail(str(e))

    # Test 7: Bắt cờ isFamily từ các Rule cues cơ bản (mẹ, cha, gia đình).
    def test_7_assertion_is_family(self):

        raw_text = "Mẹ bệnh nhân bị đái tháo đường"

        try:
            results = self.extractor.extract(raw_text)
            
            chan_doan = next((res for res in results if res.get("type") == "CHẨN_ĐOÁN"), None)
            
            assert chan_doan is not None, "Lỗi: Không trích xuất được chẩn đoán 'đái tháo đường'."

            assert "isFamily" in chan_doan.get("assertions", []), "Lỗi: Không gán được cờ 'isFamily' dù có trigger word 'Mẹ'."

        except AssertionError as e:
            pytest.fail(str(e))


    # Test 8: Đảm bảo gán nhiều cờ hợp lệ cùng lúc nếu ngữ cảnh đáp ứng (VD: tiền sử + gia đình).
    def test_8_combined_assertions(self):
        raw_text = "Bố có tiền sử cao huyết áp"
        try:
            results = self.extractor.extract(raw_text)
            
            chan_doan = next((res for res in results if res.get("type") == "CHẨN_ĐOÁN"), None)
            
            assert chan_doan is not None, "Lỗi: Không trích xuất được chẩn đoán."
            
            assertions = chan_doan.get("assertions", [])
            
            assert "isHistorical" in assertions and "isFamily" in assertions, f"Lỗi: Thiếu cờ. Kỳ vọng cả 'isFamily' và 'isHistorical', nhưng nhận được: {assertions}"
        
        except AssertionError as e:
            pytest.fail(str(e))


    # Test 9: Data Contract critical error - Nếu không có rule cue nào, assertions phải là mảng rỗng [].
    def test_9_empty_assertions_strict_type(self):
        
        raw_text = "Bệnh nhân bị đau bụng"
        
        try:
            results = self.extractor.extract(raw_text)
            
            trieu_chung = next((res for res in results if res.get("type") == "TRIỆU_CHỨNG"), None)
            
            assert trieu_chung is not None, "Lỗi: Không tìm thấy triệu chứng."
            assertions = trieu_chung.get("assertions")
            
            assert isinstance(assertions, list), "Lỗi Data Contract: trường assertions bắt buộc phải là List (mảng)."
            
            assert len(assertions) == 0, f"Lỗi Logic: Không có trigger word nhưng lại gán cờ ngẫu nhiên: {assertions}"
        
        except AssertionError as e:
            pytest.fail(str(e))


    # Test 10: Đảm bảo trích xuất chính xác trong ngữ cảnh chứa ký tự lâm sàng đặc biệt (dấu gạch chéo, dấu ngoặc).
    def test_10_robustness_with_clinical_punctuation(self):
        
        normalized_text = "bệnh nhân uống aspirin 81mg/ngày (uống sau ăn), tiền sử đái tháo đường typ 2."
        
        try:
            results = self.extractor.extract(normalized_text)
            
            thuoc = [res for res in results if res.get("type") == "THUỐC"]
            chan_doan = [res for res in results if res.get("type") == "CHẨN_ĐOÁN"]
            
            assert len(thuoc) > 0, "Lỗi: Không trích xuất được THUỐC khi liều lượng đi kèm ký tự đặc biệt '81mg/ngày'."
            
            assert any("aspirin" in e.get("text", "") for e in thuoc), "Lỗi: Regex trích xuất THUỐC bị gãy do dấu gạch chéo hoặc dấu ngoặc bổ nghĩa."
            
            assert len(chan_doan) > 0, "Lỗi: Không trích xuất được CHẨN_ĐOÁN 'đái tháo đường typ 2' chứa chữ số ở cuối."
        
        except AssertionError as e:
            pytest.fail(str(e))
        
        except Exception as e:
            pytest.fail(f"Lỗi hệ thống: Hàm extract bị crash khi xử lý ký tự đặc biệt y khoa. Chi tiết: {str(e)}")