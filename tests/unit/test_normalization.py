import pytest

class MockNormalization:
    """
    Mock class giả lập hàm chuẩn hóa văn bản của team Dev.
    Team Dev sẽ thay thế class này bằng hàm thật.
    """
    @staticmethod
    def normalize(raw_text: str) -> tuple[str, list[int]]:
        
        # Giả lập trả về chuỗi rỗng nếu đầu vào rỗng để test pass logic cơ bản
        if not raw_text:
            return "", []
        
        # Fallback giả lập (Dev sẽ implement logic chuẩn hóa Unicode, khoảng trắng, v.v. tại đây)
        return raw_text, list(range(len(raw_text)))

class TestNormalization:
    
    
    """
    Test Class kiểm định module Chuẩn hóa văn bản (Normalization).
    Đảm bảo biến đổi chuỗi thô thành chuỗi sạch và sinh offset mapping chính xác.
    """


    # Test 1: Kiểm tra loại bỏ khoảng trắng thừa liên tiếp giữa các từ
    def test_remove_extra_spaces(self):
        
        try:
            raw_text = "bệnh   trào    ngược"
            expected_text = "bệnh trào ngược"
            norm_text, mapping = MockNormalization.normalize(raw_text)
            
            assert norm_text == expected_text, f"Text chưa được chuẩn hóa khoảng trắng thừa. Nhận được: '{norm_text}'"
        
        except AssertionError as e:
            pytest.fail(f"Lỗi Logic Chuẩn Hóa: {str(e)}")
        
        except Exception as e:
            pytest.fail(f"Lỗi Hệ thống (Test 1): {str(e)}")


    # Test 2: Kiểm tra loại bỏ khoảng trắng ở đầu và cuối chuỗi (strip)
    def test_strip_leading_trailing_spaces(self):
        
        try:
            raw_text = "   đau thượng vị   "
            expected_text = "đau thượng vị"
            norm_text, mapping = MockNormalization.normalize(raw_text)
            
            assert norm_text == expected_text, f"Text chưa được strip khoảng trắng đầu/cuối. Nhận được: '{norm_text}'"
        
        except AssertionError as e:
            pytest.fail(f"Lỗi Logic Chuẩn Hóa: {str(e)}")
        
        except Exception as e:
            pytest.fail(f"Lỗi Hệ thống (Test 2): {str(e)}")


    # Test 3: Kiểm tra chuẩn hóa Unicode từ NFD sang NFC (bắt buộc cho tiếng Việt)
    def test_unicode_nfd_to_nfc(self):
        
        try:
            # Chữ "ế" ở dạng NFD (tổ hợp)
            raw_text = "t\u00ea\u0301" 
            
            # Chữ "ế" ở dạng NFC (dựng sẵn)
            expected_text = "tế" 
            
            norm_text, mapping = MockNormalization.normalize(raw_text)
            
            assert norm_text == expected_text, f"Text chưa được chuẩn hóa về Unicode NFC. Nhận được: '{norm_text}'"
        
        except AssertionError as e:
            pytest.fail(f"Lỗi Unicode: {str(e)}")
        
        except Exception as e:
            pytest.fail(f"Lỗi Hệ thống (Test 3): {str(e)}")


    # Test 4: Kiểm tra chuyển đổi ký tự tab (\t) và newline (\n) thành khoảng trắng
    def test_replace_tabs_and_newlines(self):
        
        try:
            raw_text = "bệnh\nnhân\tkhám"
            expected_text = "bệnh nhân khám"
            norm_text, mapping = MockNormalization.normalize(raw_text)
            
            assert norm_text == expected_text, f"Ký tự tab/newline chưa được xử lý. Nhận được: '{norm_text}'"
        
        except AssertionError as e:
            pytest.fail(f"Lỗi Logic Chuẩn Hóa: {str(e)}")
        
        except Exception as e:
            pytest.fail(f"Lỗi Hệ thống (Test 4): {str(e)}")


    # Test 5: Kiểm tra chuẩn hóa các dấu câu y khoa (như dấu gạch nối, dấu nháy)
    def test_normalize_special_punctuation(self):
        
        try:
            # Sử dụng dấu gạch ngang dài (em dash) cần chuẩn hóa về hyphen
            raw_text = "dạ dày—thực quản"
            expected_text = "dạ dày-thực quản"
            norm_text, mapping = MockNormalization.normalize(raw_text)
            
            assert norm_text == expected_text, f"Dấu câu đặc biệt chưa được chuẩn hóa. Nhận được: '{norm_text}'"
        
        except AssertionError as e:
            pytest.fail(f"Lỗi Logic Chuẩn Hóa: {str(e)}")
        
        except Exception as e:
            pytest.fail(f"Lỗi Hệ thống (Test 5): {str(e)}")


    # Test 6: Kiểm tra xử lý an toàn với đầu vào là chuỗi rỗng
    def test_empty_string_handling(self):
        
        try:
            raw_text = ""
            expected_text = ""
            norm_text, mapping = MockNormalization.normalize(raw_text)
            
            assert norm_text == expected_text, "Hàm không xử lý đúng chuỗi rỗng."
            
            assert mapping == [], "Offset mapping của chuỗi rỗng phải là mảng rỗng."
        
        except AssertionError as e:
            pytest.fail(f"Lỗi Boundary (Chuỗi rỗng): {str(e)}")
        
        except Exception as e:
            pytest.fail(f"Lỗi Hệ thống (Test 6): {str(e)}")


    # Test 7: Kiểm tra tính toàn vẹn khi chuỗi đầu vào đã sạch sẵn (không biến đổi)
    def test_clean_string_remains_unchanged(self):
        
        try:
            raw_text = "ho đờm xanh"
            norm_text, mapping = MockNormalization.normalize(raw_text)
            
            assert norm_text == raw_text, "Chuỗi đã sạch nhưng lại bị hàm biến đổi sai lệch."
        
        except AssertionError as e:
            pytest.fail(f"Lỗi Toàn vẹn Dữ liệu: {str(e)}")
        
        except Exception as e:
            pytest.fail(f"Lỗi Hệ thống (Test 7): {str(e)}")


    # Test 8: Kiểm tra khả năng xử lý chuỗi nhiễu phức tạp (kết hợp nhiều lỗi cùng lúc)
    def test_complex_noisy_string(self):
        
        try:
            # Chứa NFD, tab, khoảng trắng thừa, newline
            raw_text = "  b\u00ea\u0323nh   nh\u00e2n \t \n ho  "
            expected_text = "bệnh nhân ho"
            norm_text, mapping = MockNormalization.normalize(raw_text)
            
            assert norm_text == expected_text, f"Không xử lý được chuỗi nhiễu phức tạp. Nhận được: '{norm_text}'"
        
        except AssertionError as e:
            pytest.fail(f"Lỗi Logic Chuẩn Hóa: {str(e)}")
        
        except Exception as e:
            pytest.fail(f"Lỗi Hệ thống (Test 8): {str(e)}")


    # Test 9: Kiểm tra mảng offset_mapping sinh ra phải có số lượng phần tử bằng độ dài chuỗi đích
    def test_offset_mapping_length(self):
        
        try:
            raw_text = "tức   ngực"
            norm_text, mapping = MockNormalization.normalize(raw_text)
            
            assert len(mapping) == len(norm_text), f"Độ dài mapping ({len(mapping)}) không khớp với độ dài normalized text ({len(norm_text)})."
        
        except AssertionError as e:
            pytest.fail(f"Lỗi Ánh Xạ: {str(e)}")
        
        except Exception as e:
            pytest.fail(f"Lỗi Hệ thống (Test 9): {str(e)}")


    # Test 10: Kiểm tra giới hạn của phần tử trong offset_mapping không vượt quá index của chuỗi gốc
    def test_offset_mapping_boundary(self):
        
        try:
            raw_text = "ợ   hơi"
            norm_text, mapping = MockNormalization.normalize(raw_text)
            
            if len(mapping) > 0:
                max_index = max(mapping)
                assert max_index < len(raw_text), f"Offset index ({max_index}) vượt quá độ dài chuỗi gốc ({len(raw_text)})."
        
        except AssertionError as e:
            pytest.fail(f"Lỗi Out-of-Bound (Vượt giới hạn mảng): {str(e)}")
        
        except Exception as e:
            pytest.fail(f"Lỗi Hệ thống (Test 10): {str(e)}")