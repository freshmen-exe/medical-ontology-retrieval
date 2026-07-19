import os
import json
import time
import random
import copy
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# HÀM NHẬN RESPONSE
def get_json_data(url):
    ua = UserAgent()
    request_counter = 0 # Thêm biến đếm số lượng request
    url = f"https://ccs.whiteneuron.com/api/ICD10/data/type?id={id}&lang=vi"
    params = {"id": id, "lang": "vi"}
    
    # Sinh một User-Agent mới cho mỗi lần gọi hàm
    current_ua = ua.random 
    headers = {
        "User-Agent": current_ua,
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://icd.kcb.vn/",
        "Origin": "https://icd.kcb.vn"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Lỗi HTTP tại {id}: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Lỗi kết nối tại {id}: {e}")
        return None
    

# ==== CRAWL CHAPTER ====

lst_chapter_id = ['A00-B99', 'C00-D48', 'D50-D89', 'E00-E90', 'F00-F99', 'G00-G99', 'H00-H59', 
                  'H60-H95', 'I00-I99', 'J00-J99', 'K00-K93', 'L00-L99', 'M00-M99',
                  'N00-N99', 'O00-O99', 'P00-P96', 'Q00-Q99', 'R00-R99', 'S00-T98']
roman_chapters = [
    "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
    "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX"
]

json_data_chapter = {
    "name": "chapter",
    "array":[]
}
lst_include_chapter, lst_exclude_chapter = [[] for _ in range(19)], [[] for _ in range(19)]
for chapter, id, i in zip(roman_chapters, lst_chapter_id, list(range(19))):
    url = f"https://ccs.whiteneuron.com/api/ICD10/data/chapter?id={id}&lang=vi"
    response_json = get_json_data(url, id)
    if response_json is not None and response_json['status'] == 'success':
        html_content = response_json["data"]["data"]["html"]
        name = response_json["data"]["data"]["name"]
        soup = BeautifulSoup(html_content, "html.parser")
        sub_result = {
            "id": chapter,
            "parent": {
                "chapter-id": "",
                "section-id": "",
                "category-id": "",
                "sub-category-id": ""
            },
            "include": [],
            "exclude": [],
            "terms": [name]
        }

        for container in soup.select(".hover-container"):
            # Tìm thẻ quy định loại trường (include / exclude / name / code...)
            field_tag = container.find("div", class_="field")
            
            if field_tag:
                field_type = field_tag.get_text(strip=True)
                
                # Lấy text sạch từ thẻ content-raw ẩn đi kèm
                raw_text_tag = container.find("div", class_="content-raw")
                if raw_text_tag:
                    # Format text gốc thường có dạng "ID: Nội dung", dùng split để lấy phần nội dung
                    text_data = raw_text_tag.get_text(strip=True)
                    if ":" in text_data:
                        text_data = text_data.split(":", 1)[1].strip()
                    
                    # Phân loại dựa vào field_type
                    if field_type == "include":
                        sub_result['include'].append(text_data)
                        lst_include_chapter[i].append(text_data)
                    elif field_type == "exclude":
                        sub_result['exclude'].append(text_data)
                        lst_exclude_chapter[i].append(text_data)
        json_data_chapter['array'].append(sub_result)

# ==== CRAWL SECTION ====
lst_section = [
    ["A00-A09", "A15-A19", "A20-A28", "A30-A49", "A50-A64", "A65-A69", "A70-A74", "A75-A79", "A80-A89", "A92-A99", "B00-B09", "B15-B19", "B20-B24", "B25-B34", "B35-B49", "B50-B64", "B65-B83", "B85-B89", "B90-B94", "B95-B98", "B99-B99"],
    ["C00-C75", "C76-C80", "C81-C96", "C97", "D00-D09", "D10-D36", "D37-D48"],
    ["D50-D53", "D55-D59", "D60-D64", "D65-D69", "D70-D77", "D80-D89"],
    ["E00-E07", "E10-E14", "E15-E16", "E20-E35", "E40-E46", "E50-E64", "E65-E68", "E70-E90"],
    ["F00-F09", "F10-F19", "F20-F29", "F30-F39", "F40-F48", "F50-F59", "F60-F69", "F70-F79", "F80-F89", "F90-F98", "F99-F99"],
    ["G00-G09", "G10-G14", "G20-G26", "G30-G32", "G35-G37", "G40-G47", "G50-G59", "G60-G64", "G70-G73", "G80-G83", "G90-G99"],
    ["H00-H06", "H10-H13", "H15-H22", "H25-H28", "H30-H36", "H40-H42", "H43-H45", "H46-H48", "H49-H52", "H53-H54", "H55-H59"],
    ["H60-H62", "H65-H75", "H80-H83", "H90-H95"],
    ["I00-I02", "I05-I09", "I10-I15", "I20-I25", "I26-I28", "I30-I52", "I60-I69", "I70-I79", "I80-I89", "I95-I99"],
    ["J00-J06", "J09-J18", "J20-J22", "J30-J39", "J40-J47", "J60-J70", "J80-J84", "J85-J86", "J90-J94", "J95-J99"],
    ["K00-K14", "K20-K31", "K35-K38", "K40-K46", "K50-K52", "K55-K64", "K65-K67", "K70-K77", "K80-K87", "K90-K93"],
    ["L00-L08", "L10-L14", "L20-L30", "L40-L45", "L50-L54", "L55-L59", "L60-L75", "L80-L99"],
    ["M00-M03", "M05-M14", "M15-M19", "M20-M25", "M30-M36", "M40-M43", "M45-M49", "M50-M54", "M60-M63", "M65-M68", "M70-M79", "M80-M85", "M86-M90", "M91-M94", "M95-M99"],
    ["N00-N08", "N10-N16", "N17-N19", "N20-N23", "N25-N29", "N30-N39", "N40-N51", "N60-N64", "N70-N77", "N80-N98", "N99-N99"],
    ["O00-O08", "O10-O16", "O20-O29", "O30-O48", "O60-O75", "O80-O84", "O85-O92", "O95-O99"],
    ["P00-P04", "P05-P08", "P10-P15", "P20-P29", "P35-P39", "P50-P61", "P70-P74", "P75-P78", "P80-P83", "P90-P96"],
    ["Q00-Q07", "Q10-Q18", "Q20-Q28", "Q30-Q34", "Q35-Q38", "Q39-Q45", "Q50-Q56", "Q60-Q64", "Q65-Q79", "Q80-Q89", "Q90-Q99"],
    ["R00-R09", "R10-R19", "R20-R23", "R25-R29", "R30-R39", "R40-R46", "R47-R49", "R50-R69", "R70-R79", "R80-R89", "R90-R94", "R95-R99"],
    ["S00-S09", "S10-S19", "S20-S29", "S30-S39", "S40-S49", "S50-S59", "S60-S69", "S70-S79", "S80-S89", "S90-S99", "T00-T07", "T08-T14", "T15-T19", "T20-T25", "T26-T28", "T29-T32", "T33-T35", "T36-T50", "T51-T65", "T66-T78", "T79-T79", "T80-T88", "T90-T98"]
]


# =====================================================================
# VÒNG LẶP CHÍNH CÓ TÍCH HỢP SLEEP 3 LỚP
# =====================================================================

lst_include_section, lst_exclude_section = [], []
json_data_section = {
    "name": "section",
    "array": []
}

# (Giả định bạn đã khai báo roman_chapters, lst_section, lst_include_chapter, lst_exclude_chapter ở trên)

for i, (chapter, sections) in enumerate(zip(roman_chapters, lst_section)):
    lst_include_section.append([])
    lst_exclude_section.append([])
    
    for j, section in enumerate(sections):
        # 3. TĂNG BIẾN ĐẾM TRƯỚC KHI GỬI REQUEST
        request_counter += 1
        
        lst_include_section[i].append([])
        lst_exclude_section[i].append([])
        
        sub_result = {
            "id": section,
            "parent": {
                "chapter-id": chapter,
                "section-id": "",
                "category-id": "",
                "sub-category-id": ""
            },
            "include": [],
            "exclude": [],
            "terms": []
        }
        
        sub_result["include"].extend(lst_include_chapter[i])
        sub_result["exclude"].extend(lst_exclude_chapter[i])
        
        # Gửi request lấy dữ liệu
        url = f"https://ccs.whiteneuron.com/api/ICD10/data/section?id={id}&lang=vi"
        response_json = get_json_data(url, section)
        
        if response_json != "SERVER_ERROR" and response_json is not None and response_json.get('status') == 'success':
            html_content = response_json["data"]["data"]["html"]
            name = response_json["data"]["data"]["name"]
            sub_result["terms"].append(name)
            
            soup = BeautifulSoup(html_content, "html.parser")
            
            for container in soup.select(".hover-container"):
                field_tag = container.find("div", class_="field")
                
                if field_tag:
                    field_type = field_tag.get_text(strip=True)
                    raw_text_tag = container.find("div", class_="content-raw")
                    
                    if raw_text_tag:
                        text_data = raw_text_tag.get_text(strip=True)
                        if ":" in text_data:
                            text_data = text_data.split(":", 1)[1].strip()
                        
                        if field_type == "include":
                            sub_result['include'].append(text_data)
                            lst_include_section[i][j].append(text_data)
                        elif field_type == "exclude":
                            sub_result['exclude'].append(text_data)
                            lst_exclude_section[i][j].append(text_data)
                            
        json_data_section['array'].append(sub_result)

        
        # Nghỉ ngắn giữa các section (1.5 - 3.5 giây)
        time.sleep(random.uniform(1.5, 3.5))
        
        # Nghỉ dài sau mỗi 40 request (30 - 60 giây)
        if request_counter > 0 and request_counter % 40 == 0:
            sleep_time = random.uniform(30.0, 60.0)
            print(f"\n🛡️ [Anti-Ban] Bot đã chạy {request_counter} requests. Tạm nghỉ {sleep_time:.2f} giây...\n")
            time.sleep(sleep_time)
            
    # Nghỉ vừa sau khi quét xong toàn bộ section của một Chapter (5 - 10 giây)
    print(f"\n🔄 Đã xong chapter {chapter}, nghỉ một chút trước khi sang chapter mới...\n")
    time.sleep(random.uniform(5.0, 10.0))

# ==== CRAWL CATEGORY & SUB-CATEGORY ====

# 1. KHỞI TẠO BIẾN LƯU TRỮ
json_data_cate = {
    "name": "category",
    "array": []
}
json_data_sub_cate = {
    "name": "sub-category",
    "array": []
}

# 2. HÀM TẠO DANH SÁCH CATEGORY ID TỪ SECTION (Ví dụ: "A00-A09" -> ["A00", "A01", ..., "A09"])
def generate_category_ids(section_id):
    if "-" not in section_id:
        return [section_id]
    
    start, end = section_id.split("-")
    start_letter, start_num = start[0], int(start[1:])
    end_letter, end_num = end[0], int(end[1:])
    
    categories = []
    if start_letter == end_letter:
        for i in range(start_num, end_num + 1):
            categories.append(f"{start_letter}{i:02d}")
    else:
        # Xử lý trường hợp vắt chéo chữ cái (vd: A90-B09)
        for i in range(start_num, 100):
            categories.append(f"{start_letter}{i:02d}")
        for ord_l in range(ord(start_letter) + 1, ord(end_letter)):
            for i in range(100):
                categories.append(f"{chr(ord_l)}{i:02d}")
        for i in range(0, end_num + 1):
            categories.append(f"{end_letter}{i:02d}")
            
    return categories

def get_clean_text(node):
    if not node:
        return ""
    
    # 1. Nếu có thẻ div.content chuẩn thì lấy luôn (như ở thẻ li)
    content_div = node.find("div", class_="content")
    if content_div:
        return content_div.get_text(strip=True)
    
    # 2. Nếu không có (như ở thẻ tiêu đề), ta xóa rác thủ công
    temp_node = copy.copy(node) # Tránh làm hỏng cây DOM gốc
    
    # Xóa hoàn toàn khối chứa metadata ẩn
    for icon_span in temp_node.find_all("span", class_="icons"):
        icon_span.decompose()
        
    # Xóa bất kỳ thẻ nào có thuộc tính hidden
    for hidden_tag in temp_node.find_all(attrs={"hidden": True}):
        hidden_tag.decompose()
        
    return temp_node.get_text(strip=True)


# 3. VÒNG LẶP CHÍNH (Chạy từ Chapter -> Section -> Category)

for i, (chapter_roman, sections) in enumerate(zip(roman_chapters, lst_section)):
    current_chapter_id = lst_chapter_id[i]  # Ví dụ: "A00-B99"
    
    for j, section_id in enumerate(sections):  # Ví dụ: "A00-A09"
        
        # TÍNH TOÁN KẾ THỪA TỪ CHA: Cộng dồn Chapter và Section
        inherited_includes = lst_include_chapter[i] + lst_include_section[i][j]
        inherited_excludes = lst_exclude_chapter[i] + lst_exclude_section[i][j]
        
        # Tự động sinh danh sách category con: ['A00', 'A01', ..., 'A09']
        category_ids = generate_category_ids(section_id)
        
        for cat_id in category_ids:
            request_counter += 1
            print(f"Đang crawl dữ liệu Category: {cat_id}...")
            url = f"https://ccs.whiteneuron.com/api/ICD10/data/type?id={id}&lang=vi"
            response_json = get_json_data(url, cat_id)
            
            if response_json and response_json.get('status') == 'success':
                category_name = response_json["data"]["data"]["name"]
                html_content = response_json["data"]["data"]["html"]
                soup = BeautifulSoup(html_content, "html.parser")

                cate_own_includes = []
                cate_own_excludes = []

                # --- 4.1. QUÉT DỮ LIỆU CỦA CHÍNH CATEGORY ---
                for container in soup.select(".hover-container"):
                    model_tag = container.find("div", class_="model")
                    field_tag = container.find("div", class_="field")
                    
                    if model_tag and field_tag:
                        model_type = model_tag.get_text(strip=True)
                        field_type = field_tag.get_text(strip=True)
                        
                        if model_type == "type":  # Chỉ lấy của Category, chặn Sub-category
                            raw_text_tag = container.find("div", class_="content-raw")
                            if raw_text_tag:
                                text_data = raw_text_tag.get_text(strip=True)
                                if ":" in text_data:
                                    text_data = text_data.split(":", 1)[1].strip()
                                
                                if field_type == "include":
                                    cate_own_includes.append(text_data)
                                elif field_type == "exclude":
                                    cate_own_excludes.append(text_data)

                # Đóng gói Category
                sub_result_cate = {
                    "id": cat_id,
                    "parent": {
                        "chapter-id": current_chapter_id,
                        "section-id": section_id,
                        "category-id": "",
                        "sub-category-id": ""
                    },
                    "include": inherited_includes + cate_own_includes,  # Kế thừa
                    "exclude": inherited_excludes + cate_own_excludes,
                    "terms": [category_name]
                }
                json_data_cate['array'].append(sub_result_cate)

                # --- 4.2. QUÉT DỮ LIỆU SUB-CATEGORY NẰM TRONG CATEGORY NÀY ---
                sub_a_tags = []
                for a in soup.find_all("a"):
                    classes = a.get("class") or []  # SỬA LỖI: Tránh trả về None gây lỗi Crash
                    if isinstance(classes, str):
                        classes = [classes]
                    
                    # Kiểm tra lớp code định danh
                    is_code = any(c in ["code", "code-subtype", "code-disease"] for c in classes)
                    href = a.get("href", "") or ""
                    text = a.get_text(strip=True)
                    name_attr = a.get("name", "") or ""
                    
                    is_sub = False
                    if text.startswith(f"{cat_id}.") or name_attr.startswith(f"{cat_id}."):
                        is_sub = True
                    elif "disease/" in href or "subtype/" in href:
                        is_sub = True
                        
                    if is_code and is_sub:
                        sub_a_tags.append(a)

                # Duyệt qua từng mã bệnh con được tìm thấy
                for subtype_a in sub_a_tags:
                    sub_id = subtype_a.get("name") or subtype_a.get_text(strip=True)
                    sub_id = sub_id.strip()
                    
                    # Tìm thẻ cha chứa toàn bộ thông tin của subcategory này
                    parent_node = None
                    for parent in subtype_a.parents:
                        p_classes = parent.get("class") or []  # SỬA LỖI: Tránh NoneType
                        if isinstance(p_classes, str):
                            p_classes = [p_classes]
                            
                        if parent.name == "li":
                            parent_node = parent
                            break
                        # XÓA "hover-container" ra khỏi danh sách, THÊM "row" vào để bắt đúng khối chứa cả 2 cột
                        elif parent.name == "div" and any(c in ["section-disease", "disease", "section-subtype", "row"] for c in p_classes):
                            parent_node = parent
                            break
                    
                    if not parent_node:
                        parent_node = subtype_a.parent
                    
                    # Kiểm tra cấu trúc lồng nhau (Nested) hay danh sách phẳng (Flat)
                    is_nested_wrapper = False
                    if parent_node and parent_node != soup:
                        other_subs = [a for a in parent_node.find_all("a") if a in sub_a_tags and a != subtype_a]
                        if not other_subs:
                            is_nested_wrapper = True
                    
                    sub_containers = []
                    sub_lis = []
                    
                    if is_nested_wrapper:
                        sub_containers = parent_node.select(".hover-container")
                        sub_lis = parent_node.find_all("li")
                    else:
                        sibling = subtype_a.next_sibling
                        while sibling:
                            if sibling in sub_a_tags or (sibling.name == "a" and sibling in sub_a_tags):
                                break
                            if sibling.name:
                                if "hover-container" in (sibling.get("class") or []):
                                    sub_containers.append(sibling)
                                else:
                                    sub_containers.extend(sibling.select(".hover-container"))
                                    
                                if sibling.name == "li":
                                    sub_lis.append(sibling)
                                else:
                                    sub_lis.extend(sibling.find_all("li"))
                            sibling = sibling.next_sibling

                    sub_own_includes = []
                    sub_own_excludes = []
                    sub_terms = []
                    
                    # --- A. Lấy tên chính thức của bệnh con ---
                    sub_name = ""
                    if is_nested_wrapper:
                        label_tag = parent_node.find(["span", "b", "div"], class_=["label", "name", "title", "disease-name"])
                        if label_tag:
                            sub_name = get_clean_text(label_tag)
                        
                        if not sub_name:
                            b_tag = parent_node.find(["b", "strong"])
                            if b_tag:
                                sub_name = get_clean_text(b_tag)
                    
                    if not sub_name:
                        sibling = subtype_a.next_sibling
                        while sibling:
                            if sibling in sub_a_tags or (sibling.name == "a" and sibling in sub_a_tags):
                                break
                            if isinstance(sibling, str):
                                text_sibling = sibling.strip()
                                if text_sibling:
                                    sub_name = text_sibling
                                    break
                            elif sibling.name in ["span", "b", "strong"]:
                                sub_name = get_clean_text(sibling)
                                if sub_name:
                                    break
                            sibling = sibling.next_sibling
                    
                    if sub_name:
                        if sub_name.startswith(":"):
                            sub_name = sub_name[1:].strip()
                        if sub_name.startswith(sub_id):
                            sub_name = sub_name[len(sub_id):].strip()
                            if sub_name.startswith(":"):
                                sub_name = sub_name[1:].strip()
                    
                    if sub_name:
                        sub_terms.append(sub_name)
                    
                    # --- B. Quét hover-container lấy include, exclude và meaning ---
                    for container in sub_containers:
                        field_tag = container.find("div", class_="field")
                        if field_tag:
                            field_type = field_tag.get_text(strip=True)
                            raw_text_tag = container.find("div", class_="content-raw")
                            if raw_text_tag:
                                text_data = raw_text_tag.get_text(strip=True)
                                if ":" in text_data:
                                    parts = text_data.split(":", 1)
                                    if len(parts) > 1 and len(parts[0]) < 20:
                                        text_data = parts[1].strip()
                                
                                if field_type == "include":
                                    sub_own_includes.append(text_data)
                                elif field_type == "exclude":
                                    sub_own_excludes.append(text_data)
                                elif field_type in ["meaning", "index", "synonym", "term", "label"]:
                                    if text_data and text_data not in sub_terms:
                                        sub_terms.append(text_data)
                    
                    # --- C. Quét li làm từ khóa phụ (Tránh trùng lặp include/exclude) ---
                    for li in sub_lis:
                        is_inc_exc = False
                        curr = li.parent
                        while curr and curr != (parent_node if is_nested_wrapper else soup):
                            if curr.name == "div" and curr.get("class"):
                                field_div = curr.find("div", class_="field")
                                if field_div and field_div.get_text(strip=True) in ["include", "exclude"]:
                                    is_inc_exc = True
                                    break
                            curr = curr.parent
                            
                        if not is_inc_exc:
                            li_text = get_clean_text(li)  # SỬA LỖI: Gọi hàm đệ quy an toàn không lỗi DOM
                            if li_text and li_text not in sub_terms:
                                sub_terms.append(li_text)
                    
                    # --- D. Đóng gói Sub-category hoàn chỉnh ---
                    sub_result_subcate = {
                        "id": sub_id,
                        "parent": {
                            "chapter-id": current_chapter_id,
                            "section-id": section_id,
                            "category-id": cat_id,
                            "sub-category-id": ""
                        },
                        "include": sub_result_cate["include"] + sub_own_includes,
                        "exclude": sub_result_cate["exclude"] + sub_own_excludes,
                        "terms": sub_terms
                    }
                    json_data_sub_cate['array'].append(sub_result_subcate)

            # 1. Nghỉ ngắn giữa các Category (1.5 - 3.5 giây)
            time.sleep(random.uniform(1.5, 3.5))
            
            # 2. Nghỉ dài sau mỗi khoảng ngẫu nhiên từ 30 đến 50 request (Mô phỏng người dùng nghỉ ngơi)
            # Dùng random cho mốc chia hết để bot không nghỉ quá đều đặn (không nghỉ fix cứng ở số 30, 60, 90...)
            if request_counter > 0 and request_counter % 40 == 0:
                sleep_time = random.uniform(30.0, 60.0)
                print(f"🛡️ [Anti-Ban] Bot đã chạy {request_counter} requests. Tạm nghỉ {sleep_time:.2f} giây...")
                time.sleep(sleep_time)

            # 3. Nghỉ vừa sau khi quét xong một cụm Section (5 - 10 giây)
        time.sleep(random.uniform(5.0, 10.0))


# ==== EXPORT ====
json_data_chapter = {"name": "chapter", "array": []}
json_data_section = {"name": "section", "array": []}
json_data_cate = {"name": "category", "array": []}
json_data_sub_cate = {"name": "sub_category", "array": []}

# Tự động tìm thư mục gốc chứa 'icd_data' từ vị trí của file code này
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_dir = os.path.join(BASE_DIR, "icd_data", "raw_data")


data_mapping = {
    "chapter.json": json_data_chapter,
    "section.json": json_data_section,
    "category.json": json_data_cate,
    "sub_category.json": json_data_sub_cate,
}

# Tự động tạo thư mục processed_data nếu nó chưa tồn tại
os.makedirs(output_dir, exist_ok=True)

for file_name, dict_data in data_mapping.items():
    file_path = os.path.join(output_dir, file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        # ensure_ascii=False giúp hiển thị đúng tiếng Việt hoặc ký tự đặc biệt nếu có
        json.dump(dict_data, f, ensure_ascii=False, indent=4)

print(f"Đã lưu thành công 4 file JSON vào thư mục: {output_dir}")