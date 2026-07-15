# 1. Cấu trúc thư mục

```text
data/
├── icd_data/
│   ├── raw_data/          # Dữ liệu ICD-10 gốc tải về từ web
│   │   ├── chapter.json
│   │   ├── section.json
│   │   ├── category.json
│   │   └── sub-category.json
│   └── processed_data/    # Dữ liệu ICD-10 đã qua tiền xử lý, gán ID và làm sạch text
│       ├── chapter.json
│       ├── section.json
│       ├── category.json
│       └── sub-category.json
└── rxnorm_data/           # Dữ liệu RxNorm đã được trích xuất và dịch
    └── rxnorm_processed_alias.json
```

# 2. Dữ liệu ICD-10 (`icd_data`)

Dữ liệu được thu thập từ trang web chính thức của Cục Quản lý Khám, chữa bệnh (Bộ Y tế Việt Nam):

https://icd.kcb.vn/icd-10/icd10

## 2.1 Dữ liệu gốc (`raw_data`)

Chứa các file JSON nguyên bản được fetch về từ trang web, giữ nguyên cấu trúc phân cấp:

> Chapter → Section → Category → Sub-category

## 2.2 Dữ liệu đã xử lý (`processed_data`)

Các file JSON trong thư mục này đã được chuẩn hóa để phục vụ việc tìm kiếm và truy xuất (vectorization).

## 2.3 Quy tắc gắn ID

Mỗi bản ghi được gán một `id` duy nhất theo định dạng:

```text
{cấp_độ}:{mã_của_cấp_độ}:{thứ_tự_biến_thể}
```

- **Cấp độ:** Có thể là `chapter`, `section`, `category` hoặc `sub-category`.
- **Thứ tự biến thể (alias index):** Mặc định là `0`. Chỉ riêng tập `sub-category` có thể có nhiều hơn một biến thể (alias), các biến thể tiếp theo sẽ có index là `1`, `2`, ...

**Ví dụ:**

```json
"id": "section:A00-A09:0"
```

## 2.4 Quy tắc xử lý văn bản (`text`)

Trường `text` (tên của biến thể) đã được làm sạch hoàn toàn:

- Loại bỏ toàn bộ ký tự đặc biệt.
- Loại bỏ dấu tiếng Việt (unaccented).
- Chuyển toàn bộ về chữ thường (lowercase).

**Ví dụ:**

```text
"bệnh nhiễm trùng đường ruột"
→
"benh nhiem trung duong ruot"
```

## 2.5 Số lượng Vector (Kích thước mảng)

Mỗi file JSON chứa một key `"array"` bao gồm danh sách các đối tượng.

Kích thước (`length`) của mảng này tương đương với số lượng vector được tạo ra để lưu trữ embeddings.

> *Lưu ý: Có thể điền chính xác số lượng vào bảng dưới đây nếu cần.*

| File | Số lượng vector |
|------|----------------:|
| `chapter.json` | 19 |
| `section.json` | 183 |
| `category.json` | 1473 |
| `sub-category.json` | 189330 |

---

# 3. Dữ liệu RxNorm (`rxnorm_data`)

* Dữ liệu được parse từ bộ cơ sở dữ liệu UMLS RxNorm (phiên bản `RxNorm_full_prescribe_07062026_2`), tải về từ **NLM NIH RxNorm Files**.
* Số lượng vector: 109679

## 3.1 File chính

```text
rxnorm_processed_alias.json
```

## 3.2 Cấu trúc dữ liệu

Mỗi đối tượng chứa các trường thông tin sau:

- `rxnorm_id`: Định dạng `rxnorm:{rxcui}:{index}` *(Ví dụ: `"rxnorm:38:0"`).*
- `name_en`: Tên tiếng Anh nguyên bản của thuốc/hóa chất.
- `name_vi`: Tên tiếng Việt (được dịch tự động thông qua Google Translate).
- `term_type`: Phân loại thuật ngữ (Term Type - TTY).

## 3.3 Ý nghĩa của `term_type` (TTY)

Trường này đóng vai trò như một nhãn phân loại, cho biết mức độ chi tiết của chuỗi ký tự.

Ví dụ:

- `IN` (Ingredient): Tên một loại hóa chất gốc/hoạt chất. *Ví dụ:* `mesna`.
- `BN` (Brand Name): Tên được đăng ký bản quyền thương mại. *Ví dụ:* `Parlodel`.
- `SY` (Synonym): Tên đồng nghĩa.
- Các nhãn khác có thể mô tả chi tiết hình thái viên thuốc, hàm lượng và cách đóng gói.