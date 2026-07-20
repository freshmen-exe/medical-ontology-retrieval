import os
import pytest


# Giả lập hàm load_text của pipeline dev
# Khi dev viết hàm xong, hãy đổi thành: from pipeline.loaders import load_text

def load_text(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")
    with open(file_path, 'r', encoding = 'utf-8') as f:
        return f.read()


class TestTextLoader:
    
    
    # Test 1: Kiểm tra đọc file văn bản y khoa tiêu chuẩn thành công.
    def test_1_load_standard_medical_text(self, tmp_path):
    
        test_file = tmp_path / "standard.txt"
        content = "Bệnh nhân nam 70 tuổi bị bệnh 1 tuần nay, ho đờm xanh."
        test_file.write_text(content, encoding = 'utf-8')
        
        result = load_text(str(test_file))
    
        assert result == content, f"Lỗi Test 1: Đọc file cơ bản thất bại. Kỳ vọng: {content}, Thực tế: {result}"


    # Test 2: Đảm bảo tính bất biến (immutable), không tự ý xóa khoảng trắng hay khoảng thụt lề.
    def test_2_strict_immutability_preservation(self, tmp_path):
        
        test_file = tmp_path / "immutable.txt"
        content = "   Bệnh nhân   có  tiền sử   "
        test_file.write_text(content, encoding = 'utf-8')
        
        result = load_text(str(test_file))
        
        assert result == content, "Lỗi Test 2: Hàm load_text tự ý thay đổi khoảng trắng (trim/strip) làm hỏng tọa độ position của raw_text."


    # Test 3: Xử lý mượt mà các ký tự đặc biệt y khoa và tiếng Việt có dấu.
    def test_3_handle_special_and_vietnamese_characters(self, tmp_path):
        
        test_file = tmp_path / "special_chars.txt"
        content = "NEUT% (Tỷ lệ % bạch cầu trung tính):76,4; WBC:14,43 µg/L; nhiệt độ 38°C"
        test_file.write_text(content, encoding='utf-8')
        
        result = load_text(str(test_file))
        
        assert result == content, "Lỗi Test 3: Lỗi encoding khi đọc ký tự đặc biệt (%, µ, °) hoặc tiếng Việt. Cần đảm bảo chuẩn UTF-8."


    # Test 4: Giữ nguyên các dòng lộn xộn (wrapped rows) và ký tự xuống dòng (\n).
    def test_4_preserve_wrapped_rows_and_line_breaks(self, tmp_path):

        test_file = tmp_path / "wrapped_rows.txt"
        content = "Chẩn đoán:\nTrào ngược dạ dày\n\nThực quản."
        test_file.write_text(content, encoding='utf-8')
        
        result = load_text(str(test_file))

        assert result == content, "Lỗi Test 4: Hàm load_text tự ý xóa hoặc thay đổi ký tự xuống dòng (\n)."


    # Test 5: Bắt lỗi FileNotFoundError với thông báo rõ ràng khi file không tồn tại.
    def test_5_raise_error_when_file_not_found(self):

        fake_path = "non_existent_folder/fake_note.txt"
        try:
            load_text(fake_path)
            pytest.fail("Lỗi Test 5: Hệ thống không ném ra FileNotFoundError khi truyền sai đường dẫn file.")

        except FileNotFoundError:
            pass


    # Test 6: Xử lý an toàn khi file .txt hoàn toàn trống (Empty file).
    def test_6_handle_empty_file(self, tmp_path):
        
        test_file = tmp_path / "empty.txt"
        test_file.write_text("", encoding = 'utf-8')
        
        result = load_text(str(test_file))
        
        assert result == "", f"Lỗi Test 6: File trống phải trả về chuỗi rỗng. Thực tế trả về: {type(result)}"


    # Test 7: Kiểm tra độ dài chuỗi trả về khớp tuyệt đối với số ký tự gốc để phục vụ mapping tọa độ.
    def test_7_length_matching_for_position_coordinates(self, tmp_path):
        
        test_file = tmp_path / "length_check.txt"
        content = "A" * 1050 + "B" * 500  # 1550 ký tự
        test_file.write_text(content, encoding = 'utf-8')
        
        result = load_text(str(test_file))
        
        assert len(result) == 1550, f"Lỗi Test 7: Mất mát dữ liệu. Kích thước chuỗi thực tế: {len(result)}, Kỳ vọng: 1550."


    # Test 8: Đảm bảo kiểu dữ liệu trả về bắt buộc phải là chuỗi (str).
    def test_8_return_type_must_be_string(self, tmp_path):

        test_file = tmp_path / "type_check.txt"
        test_file.write_text("Hello", encoding = 'utf-8')
        
        result = load_text(str(test_file))
        
        assert isinstance(result, str), f"Lỗi Test 8: Dữ liệu trả về phải là 'str', nhưng lại nhận được {type(result)}."


    # Test 9: Giữ nguyên các ký tự Tab (\t) liên tiếp mà không tự động convert thành khoảng trắng.
    def test_9_preserve_consecutive_tabs(self, tmp_path):

        test_file = tmp_path / "tabs.txt"
        content = "WBC:\t\t14.5\tLYMPH:\t12.8"
        test_file.write_text(content, encoding='utf-8')
        
        result = load_text(str(test_file))

        assert result == content, "Lỗi Test 9: Hàm load_text tự động chuyển đổi ký tự Tab (\t) thành khoảng trắng."


    # Test 10: Đọc an toàn file chứa chuỗi cực ngắn (1 ký tự).
    def test_10_handle_single_character(self, tmp_path):

        test_file = tmp_path / "single_char.txt"
        content = "-"
        test_file.write_text(content, encoding = 'utf-8')
        
        result = load_text(str(test_file))
        
        assert result == content, f"Lỗi Test 10: Lỗi khi xử lý file cực ngắn (1 ký tự). Kỳ vọng: '{content}', Thực tế: '{result}'."