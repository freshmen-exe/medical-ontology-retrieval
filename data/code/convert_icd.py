import json
import re
import unicodedata
import itertools
import os

#  ==== HÀM CLEAN ====

# 1. Hàm xóa các mã ICD trong ngoặc (ví dụ: "( Z22 .-)", "( J00 - J22 )")
def remove_icd_codes(text):
    if not text:
        return ""
    # Regex tìm cụm: có dấu ngoặc '(', chứa 1 chữ cái + 2 chữ số (VD: Z22, J00), và kết thúc bằng ')'
    # Xóa cụm này cùng với các khoảng trắng thừa xung quanh
    cleaned_text = re.sub(r'\s*\(\s*[a-zA-Z]\d{2}[^\)]*\)', '', text)
    return cleaned_text

# 2. Hàm clean: Bỏ dấu tiếng Việt, ký tự đặc biệt và chuyển lowercase
def clean_text(text):
    if not text:
        return ""
    # Xử lý riêng chữ 'đ' và 'Đ'
    text = text.replace('đ', 'd').replace('Đ', 'D')
    # Loại bỏ dấu (diacritics)
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')
    # Loại bỏ ký tự đặc biệt (chỉ giữ lại chữ cái, số và khoảng trắng)
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    # Xóa khoảng trắng thừa và chuyển thành lowercase
    text = re.sub(r'\s+', ' ', text).strip().lower()
    return text
clean_text('hì')

# ==== HÀM TẠO BIẾN THỂ ====
# Có 3 cách chọn biến thể
# Cách 1: ko sinh biến thể cho từng term: bệnh tả (cổ điển) | châu á --> ["bệnh tả cổ điển châu á"] làm luôn trong vòng lặp, ko cần hàm
# Cách 2: sinh tổ hợp 
def generate_variants2(term):
    # Thay thế dấu '|' thành khoảng trắng để tránh dính chữ
    term = term.replace('|', ' ')
    
    # Dùng re.split để tách chuỗi an toàn không lo lỗi dấu ngoặc nhọn
    parts = re.split(r'\((.*?)\)', term)
    
    variants = []
    optionals_count = len(parts) // 2 
    
    # Sinh tổ hợp nhị phân
    for r in range(optionals_count + 1):
        for combo in itertools.combinations(range(optionals_count), r):
            keep_indices = set(combo)
            # 
            current_variant_parts = []
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    current_variant_parts.append(part)
                else:
                    optional_idx = i // 2
                    if optional_idx in keep_indices:
                        current_variant_parts.append(part)
            
            # Nối mảng lại thành chuỗi hoàn chỉnh và clean
            variant_text = "".join(current_variant_parts)
            cleaned_variant = clean_text(variant_text)
            
            if cleaned_variant not in variants:
                variants.append(cleaned_variant)
                
    return variants
generate_variants2(" Bệnh tả (Châu Á) (bệnh dịch) (ác tính) | cổ điển")

# cách 3: Không chọn cái nào trong ngoặc, Chọn từng cái một (mỗi lần 1 cái), Chọn tất cả cùng một lúc, 
# Các từ nằm ngoài ngoặc (kể cả trước/sau dấu |) đều là bắt buộc và phải luôn xuất hiện.
def generate_variants3(term):
    # Thay thế dấu '|' thành khoảng trắng. Dù có nhiều dấu '|' thì nó vẫn sẽ thành khoảng trắng
    # và được tính là phần bắt buộc nằm ngoài ngoặc.
    term = term.replace('|', ' ')
    
    # Tách chuỗi theo ngoặc đơn
    parts = re.split(r'\((.*?)\)', term)
    
    variants = []
    optionals_count = len(parts) // 2 
    
    # Tạo danh sách các trường hợp (lưu index của các từ trong ngoặc được chọn)
    valid_combinations = []
    
    if optionals_count > 0:
        # Trường hợp 1: Không chọn cái nào (tập rỗng)
        valid_combinations.append(set())
        
        # Trường hợp 2: Chọn từng cái một (mỗi tập chỉ có 1 index)
        for i in range(optionals_count):
            valid_combinations.append({i})
            
        # Trường hợp 3: Chọn tất cả (chỉ thêm vào nếu có nhiều hơn 1 từ trong ngoặc để tránh trùng lặp)
        if optionals_count > 1:
            valid_combinations.append(set(range(optionals_count)))
    else:
        # Nếu chuỗi không có ngoặc nào, chỉ có 1 trường hợp cơ bản
        valid_combinations.append(set())

    # Lắp ráp chuỗi dựa trên các trường hợp đã định nghĩa
    for keep_indices in valid_combinations:
        current_variant_parts = []
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # Vị trí chẵn: Các từ bắt buộc nằm ngoài ngoặc (Luôn lấy)
                current_variant_parts.append(part)
            else:
                # Vị trí lẻ: Các từ tùy chọn trong ngoặc
                optional_idx = i // 2
                if optional_idx in keep_indices:
                    current_variant_parts.append(part)
        
        # Nối mảng lại thành chuỗi hoàn chỉnh và clean
        variant_text = "".join(current_variant_parts)
        # Lưu ý: Bạn cần có sẵn hàm clean_text() ở ngoài để dọn dẹp khoảng trắng thừa
        cleaned_variant = clean_text(variant_text) 
        
        if cleaned_variant not in variants:
            variants.append(cleaned_variant)
            
    return variants

# ==== CONVERT ====

# 4. Hàm xử lý file từ thư mục nguồn sang thư mục đích
def process_file(input_dir, output_dir, input_filename, output_filename, type_name, version):
    input_path = os.path.join(input_dir, input_filename)
    
    if not os.path.exists(input_path):
        print(f"Không tìm thấy file: {input_path}")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    new_array = []
    
    for item in data.get('array', []):
        item_id = item.get('id', '')
        
        # Xử lý các nút parent
       # Ánh xạ dải mã ICD-10 sang số La Mã của Chapter
        chapter_map = {
            "A00-B99": "I", "C00-D48": "II", "D50-D89": "III", "E00-E90": "IV",
            "F00-F99": "V", "G00-G99": "VI", "H00-H59": "VII", "H60-H95": "VIII",
            "I00-I99": "IX", "J00-J99": "X", "K00-K93": "XI", "L00-L99": "XII",
            "M00-M99": "XIII", "N00-N99": "XIV", "O00-O99": "XV", "P00-P96": "XVI",
            "Q00-Q99": "XVII", "R00-R99": "XVIII", "S00-T98": "XIX", "V01-Y98": "XX",
            "Z00-Z99": "XXI", "U00-U85": "XXII", "U00-U99": "XXII"
        }

        # Xử lý các nút parent
        parent = item.get('parent', {})
        new_parent = {}
        for k, v in parent.items():
            if v:
                parent_type = k.replace('-id', '')
                
                # Nếu là chapter và đang ở dạng dải mã (ví dụ A00-B99) thì đổi sang số La Mã
                if parent_type == "chapter" and v in chapter_map:
                    v = chapter_map[v]
                    
                new_parent[k] = f"{parent_type}:{v}:0"
            else:
                new_parent[k] = ""
        
        # Xử lý include và exclude (GỌI HÀM remove_icd_codes TRƯỚC KHI CLEAN)
        new_include = [clean_text(remove_icd_codes(i)) for i in item.get('include', [])]
        new_exclude = [clean_text(remove_icd_codes(i)) for i in item.get('exclude', [])]
        
        # Sinh các tổ hợp biến thể từ danh sách terms
        terms = item.get('terms', [])
        unique_variants = []
        if version == 2 or version == 3:
            all_variants = []
            if version == 2:
                for term in terms:
                    all_variants.extend(generate_variants2(term))
            elif version == 3:
                for term in terms:
                    all_variants.extend(generate_variants3(term))
            for v in all_variants:
                if v not in unique_variants and v != "":
                    unique_variants.append(v)
        else:
            for term in terms:
                unique_variants.append(clean_text(term))
        # Tạo cấu trúc mới cho từng biến thể phát sinh
        for idx, variant_text in enumerate(unique_variants):
            new_item = {
                "id": f"{type_name}:{item_id}:{idx}",
                "parent": new_parent,
                "text": variant_text
            }
            new_array.append(new_item)
            
    # Đóng gói dữ liệu đầu ra
    new_data = {
        "name": data.get("name", type_name),
        "array": new_array
    }

    # Tạo thư mục đầu ra nếu chưa tồn tại
    folder_name = "data\\icd_data\\processed_data"
    output_path = os.path.join(folder_name, output_filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=4)
    print(f"Đã xử lý: {input_path} -> {output_path}", len(new_data["array"]))


# 5. Cấu hình thư mục và chạy chương trình
if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Ghép đường dẫn từ thư mục gốc vào icd_data
    INPUT_FOLDER = os.path.join(BASE_DIR, "icd_data", "raw_data")        
    OUTPUT_FOLDER = os.path.join(BASE_DIR, "icd_data", "processed_data")  
    
    # for version in range(1, 4):
    # Cấu hình file của bạn
    files_to_process = [
        ("chapter.json", "chapter_parent3.json", "chapter"),
        ("section.json", "section_parent3.json", "section"),
        ("category.json", "category_parent3.json", "category"),
        ("sub_category.json", "sub-category_parent3.json", "sub-category")
    ]
        
    for in_file, out_file, t_name in files_to_process:
        process_file(INPUT_FOLDER, OUTPUT_FOLDER, in_file, out_file, t_name, 3) # chọn varient3