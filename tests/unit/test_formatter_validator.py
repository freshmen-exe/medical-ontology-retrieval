import pytest

# Giả định đã viết hàm validate_output_format trong pipeline
from pipeline.validator import validate_output_format

class TestFormatterValidator:

    """
    Class kiểm thử bộ lọc định dạng Output (Formatter Validator).
    Đảm bảo dữ liệu JSON sinh ra khớp với Data Contract của BTC.
    
    """

    # Test 1: Kiểm tra cấu trúc chuẩn (List chứa Dict) với input giả của sample_metadata.
    def test_valid_standard_output_structure(self, sample_metadata):
        
        valid_data = [sample_metadata.copy()]
        
        # Test Positive: Nếu lỗi, Pytest tự in Traceback: "Dữ liệu chuẩn theo BTC nhưng validator lại đánh fail."
        validate_output_format(valid_data)


    # Test 2: Bắt lỗi cấu trúc root không phải là List (Ouput thẳng Dict từ sample_metadata).
    def test_invalid_root_structure_must_be_list(self, sample_metadata):
        
        invalid_root_dict = sample_metadata.copy()
        
        with pytest.raises((ValueError, TypeError)):
            
            validate_output_format(invalid_root_dict)
            
            assert False, "Lỗi nghiêm trọng: Hệ thống Validator không chặn khi Output gốc là Dict thay vì List chứa các Dict."


    # Test 3: Đảm bảo hệ thống chấp nhận đủ 5 nhãn thực thể y khoa (Type) định sẵn.
    
    @pytest.mark.parametrize("entity_type", ["TRIỆU_CHỨNG", "TÊN_XÉT_NGHIỆM", "KẾT_QUẢ_XÉT_NGHIỆM", "CHẨN_ĐOÁN", "THUỐC"])
    def test_valid_five_allowed_types(self, sample_metadata, entity_type):
        
        mock_entity = sample_metadata.copy()
        mock_entity["type"] = entity_type
        
        # Xóa candidates nếu không phải bệnh/thuốc để giữ tính hợp lệ
        if entity_type not in ["CHẨN_ĐOÁN", "THUỐC"] and "candidates" in mock_entity:
            del mock_entity["candidates"]
            
        # Test Positive: Nếu hàm từ chối nhãn hợp lệ, Pytest tự in Traceback.
        validate_output_format([mock_entity])


    # Test 4: Bắt lỗi khắt khe ném ra khi trường Type chứa nhãn rác ngoài quy định.
    def test_invalid_type_out_of_bounds(self, sample_metadata):
        
        invalid_type_data = sample_metadata.copy()
        invalid_type_data["type"] = "BỆNH_LÝ" # Nhãn rác
        
        with pytest.raises(ValueError):
            
            validate_output_format([invalid_type_data])
            
            assert False, "Thiếu chốt chặn: Validator cho phép nhãn rác 'BỆNH_LÝ' lọt qua. Chỉ được phép dùng 5 nhãn BTC quy định."


    # Test 5: Kiểm tra trường assertions chấp nhận mảng chuỗi (tối đa 3 cờ hợp lệ hoặc rỗng).
    
    @pytest.mark.parametrize("test_assertions", [
        ["isNegated", "isHistorical", "isFamily"],  # TH1: Đầy đủ 3 cờ hợp lệ
        []                                          # TH2: Mảng rỗng không có cờ nào
    ])
    
    def test_valid_assertions_string_array(self, sample_metadata, test_assertions):
        
        valid_assertions_data = sample_metadata.copy()
        valid_assertions_data["assertions"] = test_assertions
        
        # Test Positive: Nếu hàm bắt lỗi sai, Pytest tự in Traceback.
        validate_output_format([valid_assertions_data])
            

    # Test 6: Bắt lỗi khi assertions chứa boolean hoặc các cờ rác (không thuộc 3 cờ quy định).
    @pytest.mark.parametrize("invalid_assertion", [
        [True],            # Lỗi Boolean
        ["isConfirmed"]    # Lỗi cờ ngoài quy định BTC
    ])
    def test_invalid_assertions_format_and_flags(self, sample_metadata, invalid_assertion):
        
        invalid_assertion_data = sample_metadata.copy()
        invalid_assertion_data["assertions"] = invalid_assertion
        
        with pytest.raises(ValueError):
            
            validate_output_format([invalid_assertion_data])
            
            assert False, f"Thiếu chốt chặn cờ: Validator không chặn mảng assertions sai quy định: {invalid_assertion}."


    # Test 7: Bắt lỗi khi assertions chứa các cờ rác (không thuộc 3 cờ quy định).
    @pytest.mark.parametrize("missing_key", ["text", "type", "position"])
    def test_missing_required_keys(self, sample_metadata, missing_key):
        
        missing_key_data = sample_metadata.copy()
        del missing_key_data[missing_key]
        
        with pytest.raises((ValueError, KeyError)):
            
            validate_output_format([missing_key_data])
            
            assert False, f"Lỗi Data Integrity: Validator không báo lỗi khi JSON bị khuyết trường bắt buộc '{missing_key}'."


    # Test 8: Kiểm tra candidates hợp lệ theo mã chuẩn từ ICD-10 và RxNorm.
    @pytest.mark.parametrize("entity_type, mock_candidate", [
        ("CHẨN_ĐOÁN", ["A00.0"]),  # Mã ICD-10 lấy từ data thực tế
        ("THUỐC", ["360047"])      # Mã RxNorm
    ])
    
    def test_valid_candidates_for_disease_and_drug(self, sample_metadata, entity_type, mock_candidate):
        
        valid_drug_data = sample_metadata.copy()
        valid_drug_data["type"] = entity_type
        valid_drug_data["candidates"] = mock_candidate
        
        # Test Positive: Nếu hàm từ chối mã candidate hợp lệ, Pytest tự in Traceback.
        validate_output_format([valid_drug_data])


    # Test 9: Bắt lỗi khi gán candidates cho TRIỆU_CHỨNG hoặc XÉT_NGHIỆM.
    def test_invalid_candidates_assigned_to_symptom(self, sample_metadata):
        
        illegal_candidate_assignment = sample_metadata.copy()
        illegal_candidate_assignment["type"] = "TRIỆU_CHỨNG"
        
        # sample_metadata mặc định đã có sẵn 'candidates' -> Gây lỗi
        with pytest.raises(ValueError):
            
            validate_output_format([illegal_candidate_assignment])
            assert False, "Vi phạm luật BTC: Validator không chặn lỗi gán mảng 'candidates' cho nhãn 'TRIỆU_CHỨNG' hoặc 'XÉT_NGHIỆM'."
            
            
    # Test 10: Kiểm tra độ dài và logic toán học của tọa độ position (Vị trí không thể ngược hoặc âm).
    
    @pytest.mark.parametrize("invalid_position, error_desc", [
        ([15], "Thiếu phần tử end"), 
        ([121, 82], "Start lớn hơn End (Tọa độ ngược)"),
        ([-5, 10], "Tọa độ âm")
    ])
    
    def test_invalid_position_logic(self, sample_metadata, invalid_position, error_desc):
        
        invalid_position_data = sample_metadata.copy()
        invalid_position_data["position"] = invalid_position 
        
        with pytest.raises(ValueError):
            
            validate_output_format([invalid_position_data])
            
            assert False, f"Lỗi cấu trúc vị trí: Validator cho phép tọa độ sai logic ({error_desc}): {invalid_position}"