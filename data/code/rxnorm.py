import os
import json
import re
import time
from collections import defaultdict
from deep_translator import GoogleTranslator
from unidecode import unidecode

def normalize_en(text):
    text = text.lower()
    return re.sub(r'[^a-z0-9\s]', '', text).strip()

def normalize_vi(text):
    text_no_accents = unidecode(text).lower()
    return re.sub(r'[^a-z0-9\s]', '', text_no_accents).strip()

def build_translation_cache(unique_texts, cache_file="translation_cache.json", batch_size=30, sleep_time=2.5):
    """Hàm xử lý dịch theo nhóm, lưu cache liên tục và chống ban IP"""
    
    # 1. Tải cache cũ nếu có để không dịch lại từ đầu
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache = json.load(f)
    else:
        cache = {}

    # 2. Lọc ra những từ chưa có trong cache
    pending_texts = [text for text in unique_texts if text not in cache]
    
    print(f"-> Tổng số chuỗi duy nhất: {len(unique_texts)}")
    print(f"-> Đã có trong cache: {len(cache)}")
    print(f"-> Cần dịch mới: {len(pending_texts)}")

    if not pending_texts:
        return cache

    translator = GoogleTranslator(source='en', target='vi')
    
    # 3. Dịch theo từng Batch
    for i in range(0, len(pending_texts), batch_size):
        batch = pending_texts[i : i + batch_size]
        
        # Nối các từ bằng dấu xuống dòng (Google Translate giữ nguyên cấu trúc này)
        text_block = "\n".join(batch)
        
        try:
            # Gửi 1 request thay vì 30 request
            translated_block = translator.translate(text_block)
            translated_items = translated_block.split('\n')
            
            # Nếu API trả về số lượng khớp với số lượng gửi đi
            if len(translated_items) == len(batch):
                for orig, trans in zip(batch, translated_items):
                    cache[orig] = trans.strip()
            else:
                # Fallback: Nếu Google làm mất dấu xuống dòng, dịch từng từ trong batch này
                print(f"Cảnh báo batch {i}: Lệch cấu trúc, chuyển sang dịch lẻ...")
                for item in batch:
                    cache[item] = translator.translate(item).strip()
                    time.sleep(1) # Nghỉ thêm khi dịch lẻ
                    
            # Lưu cache vào ổ cứng sau mỗi mẻ
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
                
            print(f"Đã dịch {i + len(batch)} / {len(pending_texts)} (Nghỉ {sleep_time}s...)")
            time.sleep(sleep_time) # NGHỈ NHỊP CHỐNG BAN IP
            
        except Exception as e:
            print(f"Lỗi API tại batch {i}: {e}. Đang tạm nghỉ 15s để hồi phục IP...")
            time.sleep(15)

    return cache

def extract_and_build_json(rrf_path, output_json_path):
    concepts = defaultdict(lambda: {'official': None, 'tty': None, 'synonyms': set()})
    unique_texts = set()
    
    print("PHASE 1: Đọc và trích xuất dữ liệu thô...")
    if not os.path.exists(rrf_path):
        raise FileNotFoundError(f"Không tìm thấy file: {rrf_path}")
        
    with open(rrf_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('|')
            if len(parts) < 15:
                continue
                
            rxcui = parts[0]
            sab = parts[11]
            tty = parts[12]
            string_val = parts[14]
            
            if sab == 'RXNORM':
                unique_texts.add(string_val) # Thu thập từ để đem đi dịch
                
                if tty == 'SY':
                    concepts[rxcui]['synonyms'].add(string_val)
                else:
                    if concepts[rxcui]['official'] is None:
                        concepts[rxcui]['official'] = string_val
                        concepts[rxcui]['tty'] = tty

    print("\nPHASE 2: Bắt đầu quá trình Dịch máy thông minh...")
    # Bắt đầu dịch. Có thể chỉnh sửa sleep_time. Càng cao càng an toàn.
    translation_dict = build_translation_cache(list(unique_texts), cache_file="rxnorm_translate_cache.json", batch_size=40, sleep_time=2.5)
    
    print("\nPHASE 3: Lắp ráp file JSON cuối cùng...")
    result_list = []
    
    for rxcui, data in concepts.items():
        if data['official'] is None:
            continue
            
        official_name = data['official']
        vi_official = translation_dict.get(official_name, official_name)
        
        # Biến thể 0
        result_list.append({
            "rxnorm_id": f"rxnorm:{rxcui}:0",
            "name_en": normalize_en(official_name),
            "name_vi": normalize_vi(vi_official),
            "term_type": data['tty']
        })
        
        # Biến thể Synonyms
        for idx, syn in enumerate(data['synonyms'], start=1):
            vi_syn = translation_dict.get(syn, syn)
            
            result_list.append({
                "rxnorm_id": f"rxnorm:{rxcui}:{idx}",
                "name_en": normalize_en(syn),
                "name_vi": normalize_vi(vi_syn),
                "term_type": "SY"
            })
            
    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(result_list, json_file, indent=2, ensure_ascii=False)
        
    print(f"HOÀN TẤT! File đầu ra đã lưu tại: {output_json_path}")

if __name__ == "__main__":
    file_rrf_path = r"..\\RxNorm_full_prescribe_07062026_2\\rrf\\RXNCONSO.RRF"
    output_json = r"..\\rxnorm_data\\rxnorm.json"
    
    extract_and_build_json(file_rrf_path, output_json)