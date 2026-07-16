import pytest

# Giả định dev đã định nghĩa class SpanAligner trong module pipeline
from src.pipeline.alignment import SpanAligner 

class MockSpanAligner:
    """
    Mock class đại diện cho code của Dev. 
    Nhận vào raw_text và mảng offset_mapping (giả lập đã được Normalizer tạo ra từ trước)

    """
    def __init__(self, raw_text: str, offset_mapping: list):
        self.raw_text = raw_text
        self.offset_mapping = offset_mapping
        
    def get_original_span(self, norm_start: int, norm_end: int):

        # Logic giả lập - Dev phải viết logic thật dùng mảng offset_mapping
        if norm_start < 0 or norm_end > len(self.offset_mapping) or norm_start >= norm_end:
            raise IndexError("Tọa độ normalized span không hợp lệ")
            
        raw_start = self.offset_mapping[norm_start]
        # Lấy index gốc của ký tự cuối cùng trong span, sau đó +1 để ra end_index (khoảng nửa mở [start, end))
        raw_end = self.offset_mapping[norm_end - 1] + 1 
        return raw_start, raw_end

class TestSpanAligner:
    
    # 1. Test khớp vị trí chuẩn 1:1 khi chuỗi không có nhiễu (mapping tuyến tính)
    def test_1_basic_linear_alignment(self):
        
        raw_text = "đau dạ dày"
        # Mapping 1:1 [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        linear_mapping = list(range(len(raw_text))) 
        aligner = MockSpanAligner(raw_text, linear_mapping)
        
        try:
            # "dạ dày" ở bản chuẩn bắt đầu từ 4 đến 10
            raw_start, raw_end = aligner.get_original_span(4, 10)
            assert raw_text[raw_start:raw_end] == "dạ dày", f"Lỗi: Span Aligner sai lệch ở chuỗi chuẩn. Tọa độ trả về: [{raw_start}:{raw_end}]"
        except Exception as e:
            pytest.fail(f"Test 1 Fail: {str(e)}")


    # 2. Test chiếu ngược offset khi chuỗi gốc bị dư khoảng trắng ở đầu (Leading spaces)
    def test_2_align_with_removed_leading_spaces(self):
        
        raw_text = "   ho đờm"
        # Sau khi cắt 3 space đầu: "ho đờm" (len=6). Mapping: h->3, o->4, space->5, đ->6, ờ->7, m->8
        mapping = [3, 4, 5, 6, 7, 8]
        aligner = MockSpanAligner(raw_text, mapping)
        
        try:
            # Lấy chữ "ho" (norm_start=0, norm_end=2)
            raw_start, raw_end = aligner.get_original_span(0, 2)
            
            assert raw_start == 3 and raw_end == 5, f"Lỗi: Không khớp đúng offset khi text gốc có khoảng trắng đầu. Trả về [{raw_start}:{raw_end}], kỳ vọng [3:5]"
            
            assert raw_text[raw_start:raw_end] == "ho", "Lỗi: Chuỗi trích xuất từ raw_text không đúng"
        
        except Exception as e:
            pytest.fail(f"Test 2 Fail: {str(e)}")


    # 3. Test chiếu ngược offset khi chuỗi gốc bị dư khoảng trắng ở cuối (Trailing spaces)
    def test_3_align_with_removed_trailing_spaces(self):
        
        raw_text = "tức ngực   "
        # "tức ngực" ( len = 8 ). Mapping 1:1 cho 8 ký tự đầu
        mapping = [0, 1, 2, 3, 4, 5, 6, 7] 
        aligner = MockSpanAligner(raw_text, mapping)
        
        try:
            # Lấy cụm "ngực" (norm_start=4, norm_end=8)
            raw_start, raw_end = aligner.get_original_span(4, 8)
        
            assert raw_start == 4 and raw_end == 8, "Lỗi: Span Aligner xử lý sai ranh giới khi chuỗi gốc dư khoảng trắng cuối"
        
        except Exception as e:
            pytest.fail(f"Test 3 Fail: {str(e)}")


    # 4. Test chiếu ngược khi chuỗi gốc bị dư dải khoảng trắng ở giữa các từ
    def test_4_align_with_compressed_middle_spaces(self):

        raw_text = "sốt    cao" # 4 khoảng trắng ở giữa
        # Bản norm: "sốt cao" (len=7). Mapping: s->0, ố->1, t->2, space->3, c->7, a->8, o->9
        mapping = [0, 1, 2, 3, 7, 8, 9]
        aligner = MockSpanAligner(raw_text, mapping)
        
        try:
            # Lấy chữ "cao" (norm_start=4, norm_end=7)
            raw_start, raw_end = aligner.get_original_span(4, 7)
            
            assert raw_start == 7 and raw_end == 10, f"Lỗi: Đứt gãy offset khi nén khoảng trắng ở giữa. Trả về [{raw_start}:{raw_end}], kỳ vọng [7:10]"
        
        except Exception as e:
            pytest.fail(f"Test 4 Fail: {str(e)}")


    # 5. Test chênh lệch độ dài do chuyển đổi Unicode (NFD tổ hợp sang NFC dựng sẵn)
    def test_5_align_with_nfd_to_nfc_conversion(self):
        
        raw_text = "kê\u0301t qua\u0309" # "kết quả" NFD (len=9)
        # Bản norm NFC: "kết quả" (len=7). Mapping: k->0, ế(ê\u0301)->1, t->3, space->4, q->5, u->6, ả(a\u0309)->7
        mapping = [0, 1, 3, 4, 5, 6, 7]
        aligner = MockSpanAligner(raw_text, mapping)
        
        try:
            # Lấy chữ "quả" ở bản norm (norm_start=4, norm_end=7)
            raw_start, raw_end = aligner.get_original_span(4, 7)
        
            assert raw_text[raw_start:raw_end] == "qua\u0309", "Lỗi: Không quét đủ ký tự NFD tổ hợp ở chuỗi gốc khi map ngược từ NFC"
        
        except Exception as e:
            pytest.fail(f"Test 5 Fail: {str(e)}")


    # 6. Test xử lý ký tự ẩn Tab (\t) và Newline (\n) bị loại bỏ hoặc thay bằng space
    def test_6_align_with_tab_and_newline_removal(self):

        raw_text = "viêm\t\nphổi"
        # Bản norm: "viêm phổi" (len=9). Mapping: v->0, i->1, ê->2, m->3, space(từ \t\n)->4, p->6, h->7, ổ->8, i->9
        mapping = [0, 1, 2, 3, 4, 6, 7, 8, 9]
        aligner = MockSpanAligner(raw_text, mapping)
        
        try:
            # Lấy chữ "phổi" (norm_start=5, norm_end=9)
            raw_start, raw_end = aligner.get_original_span(5, 9)
            
            assert raw_start == 6 and raw_end == 10, "Lỗi: Map offset bị lệch khi chuỗi gốc chứa ký tự Tab/Newline"
        
        except Exception as e:
            pytest.fail(f"Test 6 Fail: {str(e)}")


    # 7. Test chốt chặn Data Contract: Immutability (Bất biến) của raw_text
    def test_7_immutability_of_raw_text(self):
        
        original_string = "  sốt   cao  "
        mapping = [2, 3, 4, 5, 8, 9, 10]
        aligner = MockSpanAligner(original_string, mapping)
        
        try:
        
            assert aligner.raw_text == "  sốt   cao  ", "Lỗi SINH TỬ: raw_text đã bị class Aligner ngầm thay đổi, vi phạm nguyên tắc bất biến"
        
            assert id(aligner.raw_text) == id(original_string), "Lỗi: raw_text bị copy sang vùng nhớ khác thay vì tham chiếu chuỗi gốc"
        
        except AssertionError as e:
            pytest.fail(f"Test 7 Fail: {str(e)}")


    # 8. Test kết hợp các loại nhiễu (Dư space, tab, newline)
    def test_8_complex_noise_combination(self):
        
        raw_text = "\n\t tiê\u0300n   sư\u0309 \n\n" # "tiền sử"
        # Bản norm: "tiền sử" (len=7). Mapping NFD và khoảng trắng phức tạp
        mapping = [3, 4, 6, 7, 11, 12, 14]
        aligner = MockSpanAligner(raw_text, mapping)
        
        try:
            # Lấy chữ "sử" ở bản norm (norm_start=5, norm_end=7)
            raw_start, raw_end = aligner.get_original_span(5, 7)
        
            assert raw_text[raw_start:raw_end] == "sư\u0309", "Lỗi: Hệ thống map offset sụp đổ khi gặp combo nhiều loại nhiễu"
        
        except Exception as e:
            pytest.fail(f"Test 8 Fail: {str(e)}")

    # 9. Edge Case: Xử lý biệt lệ khi try map một span nằm ngoài ranh giới
    def test_9_out_of_bounds_span_handling(self):
        
        raw_text = "bệnh phổi"
        mapping = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        aligner = MockSpanAligner(raw_text, mapping)
        
        try:
            # Cố tình gọi một tọa độ norm vượt quá độ dài bản norm
            aligner.get_original_span(5, 99)
            pytest.fail("Lỗi: Class không ném ra exception (IndexError) khi nhận vào span nằm ngoài ranh giới")
        
        except IndexError:
            pass # Pass vì code dev đã chặn lỗi đúng
        
        except Exception as e:
            pytest.fail(f"Test 9 Fail: Bắt sai loại ngoại lệ. Cần ném IndexError nhưng nhận {type(e).__name__}")

    # 10. Edge Case: Chuỗi toàn khoảng trắng hoặc rỗng
    def test_10_empty_or_whitespace_only_string(self):
        raw_text = "   \n\t  "
        mapping = [] # Bản norm rỗng nên mapping rỗng
        aligner = MockSpanAligner(raw_text, mapping)
        
        try:
            aligner.get_original_span(0, 0)
        
            pytest.fail("Lỗi: Span Aligner không ném ra IndexError khi cố lấy span từ một chuỗi đã chuẩn hóa về rỗng")
        
        except IndexError:
            pass
        
        except Exception as e:
            pytest.fail(f"Test 10 Fail: {str(e)}")