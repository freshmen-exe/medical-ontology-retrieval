import pytest

# Giả định đã viết hàm validate_output_format trong pipeline
from pipeline.validator import validate_output_format

class TestFormatterValidator:
    """
    Class kiểm thử bộ lọc định dạng Output (Formatter Validator).
    Đảm bảo dữ liệu JSON sinh ra khớp 100% với Data Contract của BTC.
    """

    # Test 1: Kiểm tra cấu trúc chuẩn (List chứa Dict) với input giả của sample_metadata.
    def test_valid_standard_output_structure(self, sample_metadata):
        valid_data = [sample_metadata.copy()]
        try:
            # Thay bằng hàm thật của dev
            validate_output_format(valid_data)
            pass
        
        except Exception as e:
            pytest.fail(f"Lỗi hệ thống: Dữ liệu chuẩn theo BTC nhưng validator lại đánh fail: {str(e)}")


    # Test 2: Bắt lỗi cấu trúc root không phải là List (Ouput thẳng Dict từ sample_metadata).
    def test_invalid_root_structure_must_be_list(self, sample_metadata):
        invalid_root_dict = sample_metadata.copy()
        try:
            # Thay bằng hàm thật của dev
            validate_output_format(invalid_root_dict)
            
            pytest.fail("Lỗi nghiêm trọng: Hệ thống Validator không chặn khi Output gốc là Dict thay vì List chứa các Dict.")
            
        except ValueError:
            pass 


    # Test 3: Đảm bảo hệ thống chấp nhận đủ 5 nhãn thực thể y khoa (Type) định sẵn.
    def test_valid_five_allowed_types(self, sample_metadata):
        
        valid_types = ["TRIỆU_CHỨNG", "TÊN_XÉT_NGHIỆM", "KẾT_QUẢ_XÉT_NGHIỆM", "CHẨN_ĐOÁN", "THUỐC"]
        try:
            for entity_type in valid_types:
                
                mock_entity = sample_metadata.copy()
                mock_entity["type"] = entity_type
                
                # Cần xóa candidates nếu không phải bệnh/thuốc để giữ tính hợp lệ cho input test
                if entity_type not in ["CHẨN_ĐOÁN", "THUỐC"] and "candidates" in mock_entity:
                    del mock_entity["candidates"]
                
                # Thay bằng hàm thật của dev
                validate_output_format([mock_entity])
                
        except Exception as e:
            pytest.fail(f"Lỗi logic: Validator từ chối nhãn hợp lệ '{entity_type}'. Chi tiết: {str(e)}")


    # Test 4: Bắt lỗi khắt khe ném ra khi trường Type chứa nhãn rác ngoài quy định.
    def test_invalid_type_out_of_bounds(self, sample_metadata):
        
        invalid_type_data = sample_metadata.copy()
        invalid_type_data["type"] = "BỆNH_LÝ" # Nhãn rác
        
        try:
            # Thay bằng hàm thật của dev
            validate_output_format([invalid_type_data])
            
            pytest.fail("Thiếu chốt chặn: Validator cho phép nhãn rác 'BỆNH_LÝ' lọt qua. Chỉ được phép dùng 5 nhãn BTC quy định.")
        
        except ValueError:
            pass

    # Test 5: Kiểm tra trường assertions chấp nhận mảng chuỗi (tối đa 3 cờ hợp lệ hoặc rỗng).
    @pytest.mark.parametrize("test_assertions", [
        ["isNegated", "isHistorical", "isFamily"],  # TH1: Đầy đủ 3 cờ hợp lệ
        []                                          # TH2: Mảng rỗng không có cờ nào
    ])
    def test_valid_assertions_string_array(self, sample_metadata, test_assertions):
        
        valid_assertions_data = sample_metadata.copy()
        valid_assertions_data["assertions"] = test_assertions
        
        try:
            # Thay bằng hàm thật của dev
            validate_output_format([valid_assertions_data])
            pass
        
        except Exception as e:
            pytest.fail(
                f"Lỗi Validator: Không chấp nhận mảng assertions hợp lệ {test_assertions}. "
                f"Chi tiết: {str(e)}"
            )
            

    # Test 6: Bắt lỗi khi assertions chứa boolean thay vì mảng chuỗi.
    def test_invalid_assertions_boolean_type(self, sample_metadata):
        
        invalid_boolean_assertion = sample_metadata.copy()
        invalid_boolean_assertion["assertions"] = [True] # Lỗi boolean
        
        try:
            # Thay bằng hàm thật của dev
            validate_output_format([invalid_boolean_assertion])
            pytest.fail("Vi phạm Data Contract: Validator đang cho phép assertions chứa Object Boolean thay vì Mảng Chuỗi.")
            
        except ValueError:
            pass


    # Test 7: Bắt lỗi khi assertions chứa các cờ rác (không thuộc 3 cờ quy định).
    def test_invalid_assertions_unauthorized_flags(self, sample_metadata):
        
        invalid_flag_assertion = sample_metadata.copy()
        invalid_flag_assertion["assertions"] = ["isConfirmed"] # Cờ lạ
        
        try:
            # Thay bằng hàm thật của dev
            validate_output_format([invalid_flag_assertion])
            pytest.fail("Thiếu chốt chặn cờ: Validator không ném lỗi khi assertions chứa cờ lạ 'isConfirmed' ngoài 3 cờ của BTC.")
            
        except ValueError:
            pass


    # Test 8: Kiểm tra trường candidates hợp lệ (là mảng chuỗi, chỉ áp dụng cho CHẨN_ĐOÁN và THUỐC).
    def test_valid_candidates_for_disease_and_drug(self, sample_metadata):
        
        valid_drug_data = sample_metadata.copy()
        valid_drug_data["type"] = "THUỐC"
        valid_drug_data["candidates"] = ["360047"] # Mã RxNorm hợp lệ
        
        try:
            # Thay bằng hàm thật của dev
            validate_output_format([valid_drug_data])
            pass
        
        except Exception as e:
            pytest.fail(f"Lỗi logic: Validator từ chối mảng candidates hợp lệ của THUỐC hoặc CHẨN_ĐOÁN. Chi tiết: {str(e)}")


    # Test 9: Bắt lỗi khi gán candidates cho TRIỆU_CHỨNG hoặc XÉT_NGHIỆM.
    def test_invalid_candidates_assigned_to_symptom(self, sample_metadata):
        
        illegal_candidate_assignment = sample_metadata.copy()
        illegal_candidate_assignment["type"] = "TRIỆU_CHỨNG"
        
        # sample_metadata mặc định đã có sẵn 'candidates' -> Gây lỗi
        
        try:
            # Thay bằng hàm thật của dev
            validate_output_format([illegal_candidate_assignment])
            pytest.fail("Vi phạm luật BTC: Validator không chặn lỗi gán mảng 'candidates' cho nhãn 'TRIỆU_CHỨNG' hoặc 'XÉT_NGHIỆM'.")
            
        except ValueError:
            pass
            
            
    # Test 10: Kiểm tra trường position bắt buộc phải là mảng chứa đúng 2 số nguyên [start, end].
    def test_invalid_position_format_and_length(self, sample_metadata):
        
        invalid_position_data = sample_metadata.copy()
        invalid_position_data["position"] = [15] # Lỗi thiếu phần tử end
        
        try:
            # Thay bằng hàm thật của dev
            validate_output_format([invalid_position_data])
            pytest.fail("Lỗi cấu trúc vị trí: Validator cho phép mảng 'position' thiếu phần tử start/end hoặc sai định dạng số nguyên.")
            
        except ValueError:
            pass