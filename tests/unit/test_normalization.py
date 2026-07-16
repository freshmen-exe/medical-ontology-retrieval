import pytest

# Giả định dev đã định nghĩa class SpanAligner trong module pipeline
# Hãy import đúng class được cài đặt thực tế vào file này
from src.pipeline.normalization import SpanAligner 


class MockSpanAligner:
    
    """
    Mock class sử dụng mã giả thay cho code của dev để tránh lỗi khi chưa có code thật.
    Cần thay thế bằng class thực tế chứa thuật toán map offset.
    """
    
    def __init__(self, raw_text: str):
        self.raw_text = raw_text
        self.normalized_view = raw_text.strip() # Giả lập logic chuẩn hóa
        
    def get_original_span(self, norm_start: int, norm_end: int):
        # Logic giả lập - Dev phải viết logic thật dùng mảng ánh xạ (offset mapping array)
        return norm_start, norm_end

class TestTextNormalizationAndAlignment:
    
    
    # 1. Kiểm tra văn bản chuẩn (không có nhiễu), offset gốc và chuẩn hóa phải khớp 1:1
    def test_1_basic_string_alignment(self):
        
        raw_text = "bệnh trào ngược dạ dày"
        aligner = MockSpanAligner(raw_text)
        
        # Giả lập tìm thấy chữ "trào ngược" ở chuỗi chuẩn hóa (index 5 -> 15)
        norm_start, norm_end = 5, 15 
        
        try:
            raw_start, raw_end = aligner.get_original_span(norm_start, norm_end)
            assert raw_text[raw_start:raw_end] == "trào ngược", "Lỗi: Không khớp đúng từ 'trào ngược' ở văn bản chuẩn 1:1"
        
        except AssertionError as e:
            pytest.fail(str(e))


    # 2. Kiểm tra loại bỏ khoảng trắng thừa ở giữa và map offset đúng về chuỗi gốc
    def test_2_extra_spaces_alignment(self):

        raw_text = "bệnh    trào   ngược" # 4 spaces and 3 spaces
        aligner = MockSpanAligner(raw_text)
        
        try:
            # Nếu chuẩn hóa đúng, "trào ngược" ở norm_text nằm ở khoảng [5:15]
            # Nhưng ở raw_text, chữ "trào" bắt đầu từ index 8, "ngược" kết thúc ở 20
            raw_start, raw_end = aligner.get_original_span(5, 15) # Giả định pass qua logic của dev

            # Code dev chuẩn phải trả về 8 và 20
            assert raw_start == 8 and raw_end == 20, "Lỗi: Offset không khớp với chuỗi gốc bị dư khoảng trắng"
        
        except AssertionError as e:
            pytest.fail(str(e))


    # 3. Kiểm tra dọn dẹp khoảng trắng ở đầu và cuối chuỗi (Leading/Trailing spaces)
    def test_3_leading_trailing_spaces(self):
        
        raw_text = "   ho đờm xanh   "
        aligner = MockSpanAligner(raw_text)
        
        try:
            # "ho" trong bản chuẩn hóa bắt đầu ở 0, kết thúc ở 2
            # Gốc phải là 3 đến 5
            
            raw_start, raw_end = aligner.get_original_span(0, 2)
            assert raw_start == 3 and raw_end == 5, "Lỗi: Không bắt đúng offset khi text gốc có khoảng trắng 2 đầu"
            
        
        except AssertionError as e:
            pytest.fail(str(e))


    # 4. Kiểm tra xử lý ký tự xuống dòng và tab (\n, \t) thành khoảng trắng
    def test_4_newline_and_tab_characters(self):
        
        raw_text = "đau\tthượng\n\nvị"
        aligner = MockSpanAligner(raw_text)
        
        try:
            # Chữ "vị" ở bản chuẩn hóa "đau thượng vị" là [11:13]
            # Gốc phải tính thêm các ký tự ẩn
            
            raw_start, raw_end = aligner.get_original_span(11, 13)
            assert raw_text[raw_start:raw_end] == "vị", "Lỗi: Offset sai lệch khi gặp ký tự Tab và Newline"
            
        except AssertionError as e:
            pytest.fail(str(e))


    # 5. Kiểm tra chuẩn hóa Unicode (NFD tổ hợp sang NFC dựng sẵn) không làm xô lệch offset
    def test_5_unicode_normalization_nfd_to_nfc(self):
        
        raw_text = "kê\u0301t qua\u0309" # "kết quả" viết bằng Unicode tổ hợp (NFD)
        aligner = MockSpanAligner(raw_text)
        
        try:
            # Độ dài chuỗi NFC ngắn hơn NFD, aligner phải chiếu ngược chính xác
            raw_start, raw_end = aligner.get_original_span(4, 7) 
            assert raw_text[raw_start:raw_end] == "qua\u0309", "Lỗi: Aligner không xử lý được chênh lệch độ dài do Unicode tổ hợp"
            
        except AssertionError as e:
            pytest.fail(str(e))


    # 6. Kiểm tra xử lý dấu câu bị dính liền (Ví dụ: dấu phẩy sát chữ)
    def test_6_punctuation_normalization(self):
        
        raw_text = "WBC:14,43;NEUT%:76,4"
        aligner = MockSpanAligner(raw_text)
        
        try:
            # Nếu norm text tự thêm dấu cách sau dấu phẩy/chấm phẩy, offset trỏ về gốc không được bao gồm khoảng trắng giả
            raw_start, raw_end = aligner.get_original_span(10, 15)
            assert raw_text[raw_start:raw_end] == "NEUT%", "Lỗi: Offset bị lệch khi tách dấu câu dính liền"
            
        except AssertionError as e:
            pytest.fail(str(e))


    # 7. Kiểm tra tính bất biến tuyệt đối (Immutable) của thuộc tính raw_text
    def test_7_raw_text_immutability(self):
        
        original_string = "  sốt   cao  "
        aligner = MockSpanAligner(original_string)
        
        try:
            assert aligner.raw_text == "  sốt   cao  ", "Lỗi ValueError: raw_text đã bị class Aligner ngầm thay đổi, vi phạm nguyên tắc bất biến"
            assert id(aligner.raw_text) == id(original_string), "Lỗi ValueError: raw_text bị copy sang vùng nhớ khác thay vì tham chiếu chuỗi gốc"
        
        except AssertionError as e:
            pytest.fail(str(e))


    # 8. Kiểm tra kết hợp phức tạp (Vừa dư khoảng trắng, vừa sai Unicode, có Tab và Newline)
    def test_8_complex_noise_combination(self):

        raw_text = "\n\t tiê\u0300n   sư\u0309 \n\n hen  suyê\u0303n  "
        aligner = MockSpanAligner(raw_text)
        
        try:
            # Trích xuất chữ "hen suyễn"
            raw_start, raw_end = aligner.get_original_span(9, 18)
            assert raw_text[raw_start:raw_end] == "hen  suyê\u0303n", "Lỗi: Hệ thống map offset sụp đổ khi gặp combo nhiều loại nhiễu"
            
        except AssertionError as e:
            pytest.fail(str(e))


    # 9. Kiểm tra Edge Case: tìm kiếm từ nằm sát rìa cuối của đoạn văn
    def test_9_edge_case_end_of_string(self):

        raw_text = "bệnh nhân bị viêm phổi   "
        aligner = MockSpanAligner(raw_text)
        
        try:
            raw_start, raw_end = aligner.get_original_span(13, 22) # "viêm phổi" ở bản norm
            assert raw_text[raw_start:raw_end] == "viêm phổi", "Lỗi: Map offset bị crash (IndexError) ở rìa cuối văn bản"
            
        except AssertionError as e:
            pytest.fail(str(e))


    # 10. Kiểm tra Edge Case: raw text toàn khoảng trắng (Empty/Whitespace-only)
    def test_10_edge_case_empty_or_whitespace_only(self):
        
        raw_text = "   \n\t  "
        aligner = MockSpanAligner(raw_text)
        
        try:
            assert aligner.normalized_view == "", "Lỗi: Normalize không quét sạch được chuỗi chỉ chứa khoảng trắng/tab"
            
            # Cố tình gọi get span trên chuỗi rỗng xem có lỗi không
            raw_start, raw_end = aligner.get_original_span(0, 0)
            
            assert raw_start == 0 and raw_end == 0, "Lỗi: Không xử lý an toàn span cho chuỗi rỗng"
        
        except Exception as e:
            pytest.fail(f"Lỗi không mong muốn khi xử lý chuỗi rỗng: {str(e)}")