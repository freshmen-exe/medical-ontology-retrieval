# Medical Ontology Retrieval

Hệ thống dự thi **Viettel AI Race 2026 - Bài 2: Ontological Reasoning in Medical Knowledge Retrieval**: phát hiện khái niệm trong văn bản y khoa tự do, suy luận ngữ cảnh, ánh xạ chẩn đoán sang **ICD-10 tiếng Việt** và thuốc sang **RxNorm**, rồi xuất đúng JSON của Ban Tổ chức (BTC).

> [!IMPORTANT]
> Repository hiện là **runtime foundation**, chưa phải pipeline hoàn chỉnh. Đã có Docker cho `Qwen3.5-4B-Q4_K_M` và `Qwen3-Embedding-0.6B-Q8_0`; chưa có code extraction, retrieval, mapping, HNSW, evaluation, app hoặc dữ liệu ontology đã chuẩn hóa. Mọi mục ghi `Kế hoạch` bên dưới là thiết kế phải triển khai và kiểm chứng, không phải tính năng đã hoàn thành.

> [!WARNING]
> Contract cuối cùng phải bám theo đề gốc tại `docs/original/Bai_2_Viettel_AI_Race_2026.{pdf,md}` (file đang nằm trong Git index tại thời điểm README này được viết). Đề yêu cầu `assertions` là **mảng chuỗi**, ví dụ `[]` hoặc `["isHistorical"]`, không phải object boolean. `position` trong ví dụ của BTC hoạt động như khoảng nửa mở `[start, end)` vì `text == raw_text[start:end]`.

## Mục Lục

- [1. Đề bài và contract bắt buộc](#1-đề-bài-và-contract-bắt-buộc)
- [2. Trạng thái, phạm vi và nguyên tắc](#2-trạng-thái-phạm-vi-và-nguyên-tắc)
- [3. Kiến trúc đích](#3-kiến-trúc-đích)
- [4. Roadmap baseline đến mạnh nhất](#4-roadmap-baseline-đến-mạnh-nhất)
- [5. Dữ liệu ICD-10 tiếng Việt](#5-dữ-liệu-icd-10-tiếng-việt)
- [6. Dữ liệu RxNorm](#6-dữ-liệu-rxnorm)
- [7. Chuẩn hóa và alias](#7-chuẩn-hóa-và-alias)
- [8. Extraction và assertion](#8-extraction-và-assertion)
- [9. Sparse, dense và hybrid retrieval](#9-sparse-dense-và-hybrid-retrieval)
- [10. HNSW từ đầu](#10-hnsw-từ-đầu)
- [11. Reranking, hierarchy và confidence](#11-reranking-hierarchy-và-confidence)
- [12. Evaluation và thí nghiệm](#12-evaluation-và-thí-nghiệm)
- [13. Runtime và cách chạy](#13-runtime-và-cách-chạy)
- [14. Cấu trúc code đề xuất](#14-cấu-trúc-code-đề-xuất)
- [15. Phân công và tiến độ](#15-phân-công-và-tiến-độ)
- [16. Definition of Done](#16-definition-of-done)
- [17. Troubleshooting](#17-troubleshooting)
- [18. Thư viện nghiên cứu](#18-thư-viện-nghiên-cứu)

## 1. Đề Bài Và Contract Bắt Buộc

### 1.1 Input và submission

- Vòng 1 cung cấp `test.zip` gồm **100** file `test/input/1.txt` đến `test/input/100.txt`.
- Mỗi input phải sinh đúng một file JSON có cùng basename.
- File nộp là `output.zip`; sau giải nén phải có `output/1.json` đến `output/100.json`.
- Top khoảng 15 đội phải giao source, data, model weights và README để BTC dựng lại trên private test.
- LLM/agent phải self-host; không gọi API mô hình ngoài; model self-host tối đa **9B parameters**.
- Vòng 1: `02/07/2026 - 30/07/2026`; tối đa 5 lượt nộp/ngày; thời gian chờ 600 giây. Vòng 2: `17-19/08/2026`; vòng 3: `09-10/09/2026`.

Nguồn nội bộ: [`đề Markdown`](docs/original/Bai_2_Viettel_AI_Race_2026.md), [`đề PDF`](docs/original/Bai_2_Viettel_AI_Race_2026.pdf).

### 1.2 Entity contract

| `type` | Ý nghĩa | `assertions` | `candidates` |
|---|---|---:|---:|
| `TRIỆU_CHỨNG` | Triệu chứng | Có | Không |
| `TÊN_XÉT_NGHIỆM` | Tên xét nghiệm | Không | Không |
| `KẾT_QUẢ_XÉT_NGHIỆM` | Giá trị và đơn vị | Không | Không |
| `CHẨN_ĐOÁN` | Chẩn đoán | Có | ICD-10 tiếng Việt |
| `THUỐC` | Thuốc/clinical drug | Có | RxNorm RXCUI |

Assertions hợp lệ: `isNegated`, `isFamily`, `isHistorical`. Chúng được biểu diễn bằng mảng chỉ chứa cờ đúng; không có cờ nào thì dùng `[]`.

```json
[
  {
    "text": "bệnh trào ngược dạ dày - thực quản",
    "type": "CHẨN_ĐOÁN",
    "candidates": ["K21.0", "K21.9"],
    "assertions": [],
    "position": [82, 121]
  }
]
```

Invariants bắt buộc:

- `text` phải là nguyên văn từ input, không phải chuỗi đã normalize.
- `position = [start, end]`, đánh số ký tự từ 0 và phải thỏa `raw_text[start:end] == text` theo ví dụ BTC.
- Candidate là **mảng**; metric Jaccard khuyến khích trả đúng tập candidate, không mặc định chỉ top-1.
- Sai `type` tạo cả false negative và false positive; theo đề, cả ba thành phần điểm của hai entity đều bằng 0.
- Không sinh entity không có trong input, ICD code/RXCUI không có trong snapshot đã load.
- Không gán candidate cho triệu chứng hoặc xét nghiệm.

### 1.3 Metric chính thức

```text
final_score = 0.3 * text_score
            + 0.3 * assertions_score
            + 0.4 * candidates_score
```

- `text_score`: trung bình `1 - WER` của trường `text`.
- `assertions_score`: Jaccard giữa hai tập assertion.
- `candidates_score`: Jaccard có trọng số theo `len(ground_truth_candidates) + 1`.
- Hai tập rỗng có Jaccard bằng 1; gold rỗng nhưng prediction không rỗng có điểm 0.

Hệ quả thiết kế:

1. Candidate chiếm trọng số cao nhất, nhưng chỉ tối ưu candidate sau khi entity/type/span đủ ổn định.
2. Boundary gần đúng vẫn có thể nhận điểm WER, nhưng local QA phải đo cả exact span để phát hiện lỗi offset.
3. Phải tune số candidate trả ra trên development set theo metric Jaccard; Recall@k cao không đồng nghĩa candidate Jaccard cao.
4. Scorer local phải tái hiện đúng matching entity của BTC trước khi dùng như leaderboard proxy.

## 2. Trạng Thái, Phạm Vi Và Nguyên Tắc

### 2.1 Hiện có

| Hạng mục | Trạng thái |
|---|---|
| `docker-compose.yml`, model cache, network nội bộ | Có |
| llama.cpp LLM server, GPU | Có cấu hình; chưa benchmark |
| llama.cpp embedding server, CPU | Có cấu hình; chưa benchmark |
| Dev Container Python 3.13 | Có |
| Đề gốc PDF/Markdown | Có trong Git index, cần giữ lại khi chốt working tree |
| Data parser, ontology snapshot | Chưa có |
| Extraction, assertions, retrieval, HNSW, mapping | Chưa có |
| Tests, scorer, benchmark, app, packaging | Chưa có |

### 2.2 Quyết định runtime hiện tại

- LLM: [`unsloth/Qwen3.5-4B-GGUF`](https://huggingface.co/unsloth/Qwen3.5-4B-GGUF), file `Qwen3.5-4B-Q4_K_M.gguf`.
- Embedding: [`Qwen/Qwen3-Embedding-0.6B-GGUF`](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B-GGUF), file `Qwen3-Embedding-0.6B-Q8_0.gguf`.
- Runtime: [`llama.cpp server`](https://github.com/ggml-org/llama.cpp/tree/master/tools/server).
- LLM dùng GPU; embedding dùng CPU; app chỉ gọi HTTP, không load model.
- Không fine-tune ở baseline. Không thêm NER/reranker neural thứ ba trước khi baseline có benchmark.
- LLM chỉ extract hoặc chọn từ whitelist; validator mới có quyền ghi code cuối.

### 2.3 Nguyên tắc kỹ thuật

- **Correctness before ANN:** exact dense là oracle/fallback; HNSW chỉ thay tốc độ, không thay semantics.
- **Candidate recall before reranking:** gold không ở top-k thì reranker không thể cứu.
- **Data before model:** lỗi source, alias, granularity và ontology version thường không sửa được bằng prompt.
- **Raw text immutable:** mọi normalization dùng view phụ kèm mapping offset.
- **Abstain instead of hallucinate:** trả candidate ít hơn hoặc không map nếu evidence yếu.
- **Version everything:** data, parser, aliases, model, prompt, index, config, scorer và commit.
- **No patient data:** chỉ dùng dữ liệu synthetic/de-identified có quyền sử dụng.

## 3. Kiến Trúc Đích

### 3.1 Offline pipeline

```text
Nguồn chính thức + checksum + license
  -> parser có provenance
  -> canonical ICD nodes / RxNorm concepts
  -> validation + manual sample review
  -> alias generation có nguồn và quality
  -> search documents
  -> sparse index + normalized embeddings
  -> exact matrix + HNSW index
  -> artifact manifests + checksums
```

### 3.2 Online pipeline

```text
immutable raw text
  -> section/sentence view + offset map
  -> dictionary/rule extraction UNION constrained-LLM extraction
  -> align span, merge, deduplicate, classify type
  -> assertion rules + selective LLM adjudication
  -> route CHẨN_ĐOÁN / THUỐC only
  -> exact aliases + char n-gram + BM25 + dense exact/HNSW
  -> collapse aliases by code
  -> Reciprocal Rank Fusion
  -> structured constraints + optional LLM whitelist selection
  -> confidence/abstention
  -> ontology whitelist + schema + span validation
  -> output/<id>.json -> output.zip
```

Fallback bắt buộc:

| Failure | Fallback |
|---|---|
| LLM invalid JSON | Retry một lần với lỗi validation, sau đó rule-only |
| LLM unavailable | Rule/dictionary extraction và deterministic ranking |
| Embedding unavailable | Exact alias + char n-gram + BM25 |
| HNSW unavailable/incompatible | Exact dense |
| Reranker lỗi | Giữ thứ tự RRF |
| Candidate invalid | Loại candidate, log lỗi |
| Final JSON invalid | Không ghi file/không tạo ZIP |

## 4. Roadmap Baseline Đến Mạnh Nhất

### B0 - Scorer và data contract

- Chép nguyên đề vào repo, khóa output schema đúng dạng array-string assertions.
- Viết validator span/type/assertions/candidates và packager 100 file.
- Viết local WER/Jaccard scorer, các toy cases có kết quả tính tay.
- Freeze dev/calibration/test trước khi tune prompt/alias.

Exit gate: perfect prediction đạt 1.0; empty/wrong-type cases đúng công thức; ZIP layout được test.

### B1 - Deterministic baseline

- Trie/dictionary/rule extraction, regex thuốc/lab/assertion.
- Exact normalized alias, diacritic-folded alias, character n-gram TF-IDF/BM25.
- ICD/RxNorm whitelist validation; chưa cần LLM hoặc HNSW.

Exit gate: pipeline chạy end-to-end, deterministic, không code giả, có error taxonomy.

### B2 - Base neural model

- Qwen3.5 constrained extraction để tăng recall; validate mọi span.
- Qwen3 embedding exact retrieval; query có task instruction.
- Sparse+dense RRF; baseline này là oracle chất lượng trước HNSW.

Exit gate: từng channel và hybrid có Recall@1/5/10/20, MRR, metric official-style và latency.

### B3 - Production baseline

- Structured drug parsing, hierarchy-aware ICD features.
- Qwen3.5 whitelist-only selection cho case mơ hồ.
- Confidence threshold và `NONE_OF_THE_ABOVE`; caching; full batch packaging.

Exit gate: selective cascade tốt hơn B2 trên frozen dev, invalid-code rate bằng 0.

### A1 - Advanced retrieval

- HNSW tự code, persistence, tombstones, exact-vs-ANN benchmark.
- Candidate diversification qua parent/child/sibling và RxNorm abstraction path.
- Calibrator riêng cho ICD và RxNorm; risk-coverage analysis.

### A2 - Advanced models

- Trial [`Qwen3-Reranker-0.6B`](https://huggingface.co/Qwen/Qwen3-Reranker-0.6B) trên CPU hoặc mutually exclusive GPU.
- Bake-off [`BGE-M3`](https://huggingface.co/BAAI/bge-m3), [`multilingual-e5-large-instruct`](https://huggingface.co/intfloat/multilingual-e5-large-instruct), [`gte-multilingual-base`](https://huggingface.co/Alibaba-NLP/gte-multilingual-base), [`SapBERT`](https://huggingface.co/cambridgeltl/SapBERT-from-PubMedBERT-fulltext).
- Chỉ đổi model nếu thắng trên bộ Vietnamese medical linking của dự án, không dựa vào MTEB chung.

### R - Research frontier

- Hard-negative mining và contrastive fine-tuning sau khi có gold đủ sạch.
- BioSyn/SapBERT-style synonym alignment, multilingual-biomedical ensemble.
- Joint document inference, graph/hierarchy regularization, hyperbolic ontology embedding.
- Conformal candidate sets và distribution-shift monitoring.

Không chuyển stage nếu stage trước chưa có benchmark và error analysis.

## 5. Dữ Liệu ICD-10 Tiếng Việt

### 5.1 Nguồn authoritative

Target hiện hành của dự án là **Thông tư 06/2026/TT-BYT**, ban hành `02/04/2026`, hiệu lực `01/07/2026`, không phải ICD-10-CM:

- [Cổng Thông tin điện tử Chính phủ](https://chinhphu.vn/?docid=217536&pageid=27160)
- [Thông tư PDF](https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/4/06-byt.pdf)
- [Phụ lục ICD-10 tiếng Việt PDF](https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/4/06-byt-kem.pdf)
- [Hệ thống tra cứu ICD của Cục Quản lý Khám, chữa bệnh](https://icd.kcb.vn/icd-10/icd10), chỉ dùng cross-check, không thay artifact gốc
- [WHO ICD-10 Browser 2019](https://icd.who.int/browse10/2019/en), kiểm tra cấu trúc quốc tế, không thay nhãn tiếng Việt
- [WHO ICD-10 Volume 2](https://icd.who.int/browse10/Content/statichtml/ICD10Volume2_en_2019.pdf), quy tắc coding
- [WHO ICD API](https://icd.who.int/icdapi), cần đăng ký và phải kiểm tra release/language hỗ trợ

### 5.2 Acquisition manifest

Mỗi file raw phải ghi: authority, title, number, issue/effective date, URL, retrieval timestamp, filename, byte size, publisher checksum nếu có, local SHA-256, media type, license/redistribution note, parser commit, known issues. Raw file bất biến; sửa lỗi bằng parser, không sửa tay PDF.

### 5.3 Canonical node

```json
{
  "code_raw": "K21.9",
  "code_normalized": "K219",
  "title_vi": "Bệnh trào ngược dạ dày-thực quản không viêm thực quản",
  "level": "subcategory",
  "parent_code": "K21",
  "chapter": "XI",
  "block": "K20-K31",
  "inclusion": [],
  "exclusion": [],
  "instruction": [],
  "source_page": 0,
  "source_version": "06/2026/TT-BYT",
  "review_status": "parsed"
}
```

Parser phải xử lý wrapped rows, repeated headers, merged cells, OCR `0/O`, `1/I/l`, dấu tiếng Việt, dagger/asterisk, chapter/block/category/subcategory và heading không codeable. Không suy parent chỉ bằng cắt chuỗi; lưu edge và nguồn assertion riêng.

### 5.4 Legal boundary

- Không có license mở rõ ràng được xác nhận cho bản chuyển đổi toàn bộ phụ lục; trước khi redistribute CSV/JSON hoặc embedding labels phải review quyền sử dụng.
- MIT của repo không cấp lại quyền cho dữ liệu Bộ Y tế/WHO.
- Không dùng license ICD-11 để suy ra license ICD-10.
- Có thể phát hành parser + manifest + checksum riêng, giữ raw/processed corpus ngoài Git nếu quyền phân phối chưa rõ.

## 6. Dữ Liệu RxNorm

### 6.1 Snapshot được pin

Tại ngày `14/07/2026`, NLM công bố:

| Gói | Ngày | Checksum NLM | Quyền truy cập |
|---|---|---|---|
| [`RxNorm_full_07062026.zip`](https://download.nlm.nih.gov/umls/kss/rxnorm/RxNorm_full_07062026.zip) | 06/07/2026 | MD5 `33acdc0176af35808f91b3fc74ff2bb4` | Cần UMLS license |
| [`RxNorm_full_prescribe_07062026.zip`](https://download.nlm.nih.gov/rxnorm/RxNorm_full_prescribe_07062026.zip) | 06/07/2026 | MD5 `767678e3b5b1d6fe358b61c21659f3ef` | NLM ghi không cần license |

Nguồn bắt buộc đọc:

- [Release/download page](https://www.nlm.nih.gov/research/umls/rxnorm/docs/rxnormfiles.html)
- [Release notes full 07/2026](https://www.nlm.nih.gov/research/umls/rxnorm/docs/2026/rxnorm_releasenotes_full_07062026.html)
- [Technical documentation](https://www.nlm.nih.gov/research/umls/rxnorm/docs/techdoc.html)
- [Term types](https://www.nlm.nih.gov/research/umls/rxnorm/docs/appendix5.html)
- [Relationships](https://www.nlm.nih.gov/research/umls/rxnorm/docs/appendix1.html)
- [Terms of Service](https://www.nlm.nih.gov/research/umls/rxnorm/docs/termsofservice.html)
- [UMLS licensing/access](https://www.nlm.nih.gov/databases/umls.html)
- [Automated downloads](https://documentation.uts.nlm.nih.gov/automating-downloads.html)
- [RxNorm API](https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html) và [API terms/rate limit](https://lhncbc.nlm.nih.gov/RxNav/TermsofService.html)

Luôn lưu dated artifact, MD5 để đối chiếu NLM và SHA-256 nội bộ; không dùng URL `current` làm provenance cuối.

### 6.2 Files cần parse

| File | Dùng để làm gì |
|---|---|
| `RXNCONSO.RRF` | RXCUI, RXAUI, `SAB`, `TTY`, `STR`, `SUPPRESS`, `CVF` |
| `RXNREL.RRF` | ingredient, dose form, brand, component, quantified-form graph |
| `RXNSAT.RRF` | NDC, quantity, qualitative distinction và attributes |
| `RXNSAB.RRF` | source/version/restriction metadata |
| `RXNDOC.RRF` | định nghĩa enum thay vì hard-code mù |
| `RXNCUI.RRF` | lịch sử retired dispensable RXCUI |
| `RXNATOMARCHIVE.RRF` | atom đã archive |
| `RXNCUICHANGES.RRF` | thay đổi RXCUI giữa hai release |

RRF là UTF-8, pipe-delimited và có terminal pipe. Parser phải kiểm tra đúng số cột.

### 6.3 TTY và mapping level

| TTY | Ý nghĩa |
|---|---|
| `IN`, `PIN`, `MIN` | ingredient, precise ingredient, multi-ingredient |
| `BN` | brand name, không phải clinical drug đầy đủ |
| `DF`, `DFG` | dose form và group |
| `SCDF`, `SBDF` | ingredient + form, chưa đủ strength |
| `SCD`, `SBD` | semantic/branded clinical drug |
| `GPCK`, `BPCK` | generic/branded pack |

Backoff an toàn:

```text
exact branded drug -> semantic clinical drug -> ingredient+form/strength
-> ingredient only -> unmapped
```

Không báo ingredient fallback như exact product match. Lưu `mapping_level` nội bộ dù output BTC chỉ nhận RXCUI.

### 6.4 Filters và license

- `SUPPRESS` có `N`, `O`, `Y`, `E`; không cast thành boolean.
- `CVF=4096` biểu thị Current Prescribable Content.
- `SAB=RXNORM` là normalized NLM content; source atom khác có restriction riêng.
- Một RXCUI chứa atom public-domain lẫn restricted không làm mọi atom tự do phân phối.
- Current Prescribable Content là xấp xỉ thuốc đang lưu hành tại Mỹ, không phải danh mục thuốc Việt Nam.
- Biệt dược Việt có thể thiếu; tạo alias có provenance rồi map về mức RxNorm được evidence hỗ trợ.

API spot checks: [`/REST/version`](https://rxnav.nlm.nih.gov/REST/version.json), `/REST/rxcui/{id}/properties.json`, `/historystatus.json`, `/approximateTerm.json`. Không dùng API online làm production dependency nếu cần self-contained; NLM giới hạn 20 request/s/IP và khuyên cache 12-24 giờ.

## 7. Chuẩn Hóa Và Alias

Giữ ba lớp:

1. `raw_text`: bất biến, dùng output và offset.
2. `normalized_view`: NFC, whitespace/punctuation/unit normalization có offset map.
3. `retrieval_views`: lower-case, diacritic-folded, token/character n-gram, structured attributes.

Safe transforms:

- Unicode NFC; chuẩn hóa whitespace, hyphen/slash và dấu nháy.
- Biến thể có/không dấu nhưng không thay raw output.
- Decimal comma/dot và unit canonicalization (`mcg`, `µg`, `ug`; `mg/ml`).
- Viết tắt lâm sàng/đường dùng/tần suất được review (`po`, `bid`, `qid`, `prn`).
- Salt/base, generic/brand, dose form và release-type variants có provenance.
- Vietnamese-English code-switch aliases có kiểm tra.

Mỗi alias cần `alias`, `concept_id`, `system`, `source_type`, `source`, `source_version`, `quality`, `review_status`, `collision_count`. Alias LLM-generated chỉ là weak retrieval document cho đến khi review; không được tự động thành exact mapping.

Reject/quarantine alias nếu làm mất laterality, anatomical site, acuity, etiology, strength, route, release type, form hoặc đổi child thành parent. Index alias riêng và aggregate về concept, thường dùng `max(alias_score)` trước khi fusion.

Nguồn dữ liệu phụ:

- [`PhoNER_COVID19`](https://github.com/VinAIResearch/PhoNER_COVID19), [paper NAACL 2021](https://aclanthology.org/2021.naacl-main.173/): Vietnamese NER chất lượng, nhưng research/education only và cấm redistribution; không phải clinical-note linking corpus.
- [`ViMQ`](https://github.com/tadeephuy/ViMQ), [paper](https://link.springer.com/chapter/10.1007/978-3-030-92310-5_76): không thấy license dataset rõ ràng; phải xin phép trước reuse/derivative/redistribution.
- Không coi GitHub/Hugging Face visibility là license.

## 8. Extraction Và Assertion

### 8.1 Baseline rule/dictionary

- Trie/Aho-Corasick cho ontology labels và reviewed aliases.
- Regex thuốc: tên, ingredient, strength, unit, concentration, form, route, frequency, duration.
- Regex lab name/result, giữ tên và kết quả thành entity riêng theo đề.
- Longest match nhưng giữ nested candidate nếu product và ingredient có nghĩa riêng.
- Section detector cho chẩn đoán, tiền sử, gia đình, thuốc trước nhập viện, dị ứng, kế hoạch.

### 8.2 Assertion schema nội bộ

Nội bộ nên giàu hơn output để tránh ép mất thông tin:

```text
polarity: affirmed | negated
certainty: certain | probable | possible | unlikely | unknown
temporality: current | historical | future | resolved | unknown
experiencer: patient | family | other | unknown
conditionality: actual | hypothetical | conditional
```

Cuối pipeline chỉ project về ba cờ BTC.

Rule cues ban đầu:

- Negation: `không`, `chưa`, `không ghi nhận`, `không thấy`, `loại trừ`, `âm tính với`.
- Uncertainty: `nghi`, `theo dõi`, `có thể`, `khả năng`, `chưa loại trừ`.
- Historical: `tiền sử`, `đã từng`, `trước đây`, `đã khỏi`.
- Family: `mẹ`, `cha`, `bố`, `gia đình`, `người nhà`.
- Hypothetical/planned: `nếu`, `cân nhắc`, `dự kiến`, `tầm soát`, `phòng ngừa`.

Phải có pre/post trigger, clause termination, pseudo-trigger, coordination scope và section defaults. Nền tảng: [NegEx](https://pubmed.ncbi.nlm.nih.gov/12123149/), [ConText](https://doi.org/10.1016/j.jbi.2009.05.002), [historical context](https://aclanthology.org/W09-1302/).

### 8.3 Qwen3.5 extraction

- Chunk theo section nhưng giữ global offsets.
- Dùng JSON-schema-constrained output của [llama.cpp server](https://github.com/ggml-org/llama.cpp/tree/master/tools/server).
- Model trả exact surface + offsets + type + context evidence, không trả ICD/RXCUI.
- Validator reject span nếu `raw[start:end] != text`, overlap policy sai hoặc type ngoài enum.
- Union rule và LLM để tăng recall; merge deterministic.
- Bulk extraction nên thử thinking off; chỉ dùng thinking cho case assertion/selection khó và đo latency.

Minimal-pair tests bắt buộc: `có/không viêm phổi`, `tiền sử/hiện tăng huyết áp`, `mẹ/bệnh nhân bị đái tháo đường`, `theo dõi/chẩn đoán lao phổi`.

## 9. Sparse, Dense Và Hybrid Retrieval

### 9.1 Exact và character baseline

- Exact alias map là channel riêng với ưu tiên cao nhưng phải xử lý collisions.
- Character 3-5 gram TF-IDF chịu được mất dấu, lỗi spacing, typo và brand transliteration.
- Fit IDF chỉ trên ontology/index corpus, không lấy test mentions làm aliases.
- Công thức/thực hành: [Stanford IR book](https://nlp.stanford.edu/IR-book/), [TF-IDF](https://nlp.stanford.edu/IR-book/html/htmledition/inverse-document-frequency-1.html), [vector scoring](https://nlp.stanford.edu/IR-book/html/htmledition/vector-space-classification-1.html).

### 9.2 BM25 tự code

```text
score(D,Q) = sum IDF(q) * f(q,D)*(k1+1)
             / (f(q,D) + k1*(1-b+b*|D|/avgdl))
```

Ghi rõ IDF variant, smoothing, `k1`, `b`, tokenizer và duplicate-query-term policy. Start grid: `k1 in {0.8,1.2,1.5,2.0}`, `b in {0,0.5,0.75,1}`. Nguồn: [Robertson & Zaragoza](https://doi.org/10.1561/1500000019), [author PDF](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf), [Lucene reference implementation](https://github.com/apache/lucene/blob/main/lucene/core/src/java/org/apache/lucene/search/similarities/BM25Similarity.java).

### 9.3 Dense exact

- Qwen3-Embedding-0.6B: 1024d, last-token pooling, 100+ languages, instruction-aware; [official GGUF card](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B-GGUF), [paper](https://arxiv.org/abs/2506.05176), [repo](https://github.com/QwenLM/Qwen3-Embedding).
- L2-normalize document vectors và query; cosine bằng dot product; reject zero/NaN/Inf vectors.
- Index documents không thêm instruction. Query dùng English task instruction theo khuyến nghị model card.

```text
Instruct: Given a Vietnamese clinical disease or symptom mention in context,
retrieve the most specific valid concept from the official Vietnamese ICD-10
catalogue. Prefer supported diagnoses and abstain from unsupported specificity.
Query: <mention + short context>
```

```text
Instruct: Given a Vietnamese medication mention, retrieve the matching RxNorm
concept using ingredient, strength, dose form, route, and brand when available.
Query: <structured medication>
```

Thử mention-only, mention+sentence, canonical attributes và section context. Exact dense dùng batched matrix multiplication và `argpartition`; đây là ground truth ANN.

### 9.4 Code-level RRF

Trước fusion, mỗi channel collapse alias về best rank của **concept/code**, không cho nhiều alias của một code chiếm nhiều phiếu.

```text
RRF(code) = sum_channel 1 / (rrf_k + rank_channel(code))
```

Start `rrf_k=60`, rank bắt đầu từ 1; document vắng channel đóng góp 0; tie-break bằng stable code ID. Nguồn gốc: [Cormack et al., SIGIR 2009](https://doi.org/10.1145/1571941.1572114), [paper PDF](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf).

So sánh bắt buộc: exact-only, char-only, BM25-only, dense-only, sparse fusion, sparse+dense RRF. Không cộng raw cosine và BM25 trực tiếp nếu chưa calibration.

## 10. HNSW Từ Đầu

### 10.1 Nguồn phải đọc

- [Paper gốc HNSW](https://arxiv.org/abs/1603.09320), [PDF](https://arxiv.org/pdf/1603.09320), [IEEE DOI](https://doi.org/10.1109/TPAMI.2018.2889473).
- [NMSLIB implementation dùng trong nghiên cứu](https://github.com/nmslib/nmslib/blob/master/similarity_search/src/method/hnsw.cc).
- [`hnswlib` core `hnswalg.h`](https://github.com/nmslib/hnswlib/blob/master/hnswlib/hnswalg.h), [parameter guide](https://github.com/nmslib/hnswlib/blob/master/ALGO_PARAMS.md), [recall tests](https://github.com/nmslib/hnswlib/blob/master/TESTING_RECALL.md), [Python tests](https://github.com/nmslib/hnswlib/tree/master/tests/python).
- [ANN-Benchmarks paper](https://arxiv.org/abs/1807.05614), [ANN-Benchmarks](https://github.com/erikbern/ann-benchmarks), [VIBE](https://github.com/vector-index-bench/vibe), [Big ANN Benchmarks](https://github.com/harsha-simhadri/big-ann-benchmarks).

Không dùng hnswlib làm lời giải core nếu mục tiêu là tự code; dùng nó làm behavioral reference/benchmark.

### 10.2 Data structures và invariants

```text
vectors[N, d]: float32 normalized
levels[N]: int32
links[level][node] -> unique neighbor IDs
deleted[N]: bool
entry_point: int | None
max_level: int
M, M0=2*M, ef_construction, ef_search, seed
```

Invariants: không self-loop/duplicate; neighbor tồn tại ở layer; degree layer 0 `<=M0`, layer cao `<=M`; node level `L` tồn tại ở `0..L`; entry point thuộc max layer; metric luôn theo convention **smaller is better**.

Cosine trên normalized vectors: `distance = 1 - x @ y`. Squared L2 không cần căn. Với unit vectors, cosine/IP/L2 cho cùng ranking. Tham khảo [Faiss metric semantics](https://github.com/facebookresearch/faiss/wiki/MetricType-and-distances).

### 10.3 Random level

```text
mL = 1 / ln(M)
level = floor(-ln(U) * mL), U ~ Uniform(0,1]
P(level >= l) ~= M^(-l)
```

Dùng `np.random.default_rng(seed)`, clamp `U` khỏi 0, insertion order cố định. Test tail distribution thay vì equality tuyệt đối.

### 10.4 Search layer

```text
search_layer(query, entry_points, ef, level):
  visited = entry_points
  candidates = min_heap by (distance, id)
  results = bounded max_heap size ef
  while candidates:
    c = nearest candidate
    if results full and distance(c) > worst(results): break
    for neighbor not visited:
      mark visited immediately
      if results not full or neighbor better than worst:
        push candidates and results; trim results to ef
  return results sorted best-first
```

Lỗi phổ biến nhất là đảo heap, stop trước khi result đủ `ef`, mark visited quá muộn và dùng similarity ở code giả định distance.

### 10.5 Neighbor heuristic và insertion

Xét candidate từ gần new node nhất; chỉ nhận `e` nếu với mọi neighbor đã chọn `r`, `d(e,r) >= d(e,q)`. Đây là diversity heuristic; fallback nearest candidates nếu chưa đủ `M`.

Insertion:

1. Sample level cho node mới; node đầu trở thành entry point.
2. Từ `max_level` xuống trên level mới: greedy descent với `ef=1`.
3. Từ `min(new_level,max_level)` xuống 0: `search_layer(..., ef_construction)`, select tối đa `M`, thêm connections hai chiều.
4. Khi backlink vượt capacity, rerun diversity heuristic quanh node nhận link; layer 0 cap `M0`, layer trên cap `M`.
5. Nếu level mới cao hơn, cập nhật entry point/max level.

Tie-break mọi nơi bằng ID. Ghi rõ policy nếu pruning làm graph không hoàn toàn symmetric; bản baseline nên ưu tiên invariant dễ kiểm tra.

### 10.6 Query, deletion và persistence

- Greedy từ max layer xuống layer 1; layer 0 chạy beam với `ef=max(ef_search,k)`.
- Tombstone vẫn được traversal nhưng không được trả kết quả; hard delete nên rebuild/compact.
- Không ghi đè vector vào slot deleted mà giữ links cũ.
- Persistence phải có magic/version, endianness, dtype, dim, metric, params, vectors, levels, deleted, labels, adjacency, entry point và checksum; load phải validate range/degree/version.

### 10.7 Tuning và benchmark

- Start `M in {8,16,24,32}`, `efConstruction in {100,200,400}`, `efSearch in {k,2k,4k,8k,16k,32k}`.
- Báo clinical Recall@k so với qrels **và** ANN overlap Recall@k so với exact dense; đây là hai metric khác nhau.
- Báo build time, index bytes, peak RSS, p50/p95/p99, QPS, distance computations và recall-latency-memory Pareto frontier.
- Không benchmark query là chính indexed vector vì self-match làm bài toán dễ giả.

Unit/property tests: metric, zero vector, random levels, hand-built chain/ring/clusters, duplicate vectors, ties, deleted bridge, `ef` boundaries, insertion invariants, save/load round trip, corrupt file, exact recall. Có thể tham khảo [Hypothesis](https://hypothesis.readthedocs.io/) để sinh case, nhưng thuật toán vẫn do team viết.

## 11. Reranking, Hierarchy Và Confidence

### 11.1 Deterministic constraints

- Candidate phải thuộc đúng ontology snapshot và entity family.
- ICD non-selectable heading bị loại nếu output cần codeable node.
- Không chọn child nếu text thiếu qualifier phân biệt; dùng parent hợp lệ hoặc abstain.
- RxNorm ingredient mismatch là hard/strong reject; strength, unit, form, route, release type, brand là explicit features.
- Loại suppressed/obsolete RXCUI theo policy; resolve history thay vì chấp nhận mù.

### 11.2 Qwen3.5 whitelist selection

Chỉ gọi cho case low-margin/ambiguous. Cung cấp 5-15 candidate với ID, label, alias, parent path/notes; RxNorm thêm TTY, ingredient, strength, form, route, brand. Luôn có `NONE_OF_THE_ABOVE`.

```json
{
  "selected_candidate_ids": ["candidate-from-list"],
  "decision": "exact",
  "evidence": ["ingredient and strength match"],
  "contradictions": []
}
```

Validator không chấp nhận ID ngoài list. Cache key phải chứa normalized mention, context, candidate-list hash, model hash và prompt version. Candidate order randomization là ablation bắt buộc để phát hiện positional bias.

### 11.3 Graph reasoning

- ICD: depth, ancestor path, selectable status, chapter/block, sibling ambiguity, evidence-supported specificity.
- RxNorm: `has_ingredient`, `has_dose_form`, `tradename_of`, `consists_of`, `contains`, `has_quantified_form` và reciprocal relationships.
- Document coherence chỉ dùng evidence an toàn như repeated mentions, abbreviation expansion và brand-ingredient agreement; không áp disease co-occurrence prior từ dữ liệu không phù hợp.

### 11.4 Calibration và abstention

Features: channel scores/ranks, top1-top2 margin, channel agreement, alias provenance/collision, structured compatibility, candidate entropy, hierarchy ambiguity, LLM agreement và stability giữa query variants.

Train calibrator riêng ICD/RxNorm trên calibration split. Start logistic/Platt; isotonic khi data đủ. LLM prose confidence không phải probability. Tài liệu: [Guo et al.](https://proceedings.mlr.press/v70/guo17a.html), [scikit-learn calibration guide](https://scikit-learn.org/stable/modules/calibration.html), [selective classification](https://proceedings.neurips.cc/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Abstract.html), [conformal introduction](https://arxiv.org/abs/2107.07511).

## 12. Evaluation Và Thí Nghiệm

### 12.1 Split và leakage

- Split patient > encounter > document; không split mention ngẫu nhiên nếu cùng note/patient.
- Tách train, dev, calibration, frozen test và OOD/challenge.
- Audit exact/normalized hashes, paragraph/sentence duplicates, template copying, near duplicates.
- Ontology full catalogue được dùng inference là hợp lệ; thêm gold test surface vào alias table là leakage.
- Báo seen concept, unseen concept, unseen alias, rare/head và ontology drift riêng.

### 12.2 Component metrics

| Layer | Metrics |
|---|---|
| Extraction | exact/IoU relaxed span P/R/F1, typed F1, per-type/macro F1 |
| Assertions | oracle-span và predicted-span F1 cho từng cờ, tuple accuracy |
| Retrieval | Recall@1/5/10/20, MRR, MAP khi multi-relevant, nDCG graded |
| Mapping | exact ICD/RXCUI accuracy, candidate Jaccard, hierarchy/component diagnostics |
| End-to-end | exact mention+type+assertion+concept micro F1, document set F1 |
| Calibration | Brier, log loss, ECE + reliability diagram, risk-coverage |
| Efficiency | cold/warm p50/p95/p99, throughput, RAM/VRAM, index/build/load size/time |
| Competition | WER/Jaccard `0.3/0.3/0.4`, chỉ gọi official proxy khi scorer khớp BTC |

Span matching phải one-to-one; relaxed matching nên dùng maximum-weight bipartite matching, không greedy mơ hồ. Tools tham khảo: [`nervaluate`](https://github.com/MantisAI/nervaluate), [`seqeval`](https://github.com/chakki-works/seqeval), [CoNLL NER metric](https://aclanthology.org/W03-0419/).

Retrieval qrels dùng `query_id`, concept, relevance. Nếu graded: 3 exact, 2 acceptable equivalent, 1 fallback/ancestor, 0 wrong; policy phải clinician/coder review. Công thức và tools: [Stanford IR evaluation](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-in-information-retrieval-1.html), [nDCG paper](https://doi.org/10.1145/582415.582418), [`trec_eval`](https://github.com/usnistgov/trec_eval), [`ir_measures`](https://ir-measur.es/), [`ranx`](https://github.com/AmenRa/ranx).

### 12.3 Experiment matrix tối thiểu

| ID | Cấu hình | Mục đích |
|---|---|---|
| E0 | rule/dictionary | extraction floor |
| E1 | Qwen constrained | neural extraction |
| E2 | rule UNION Qwen | high-recall extraction |
| R0 | exact alias | lexical floor |
| R1 | char n-gram | noisy Vietnamese |
| R2 | BM25 | token lexical retrieval |
| R3 | Qwen dense exact | dense oracle |
| R4 | sparse+dense RRF | hybrid baseline |
| R5 | R4+HNSW | ANN quality/speed loss |
| S0 | retriever top-1/top-n | no-reranker baseline |
| S1 | deterministic constraints | structured mapping |
| S2 | Qwen whitelist selector | selective reranking |
| S3 | calibrated S2 | safety/coverage |
| P0-P3 | kết hợp tốt nhất từng stage | end-to-end progression |

Ablations bắt buộc: query instruction, mention/context form, accents, alias groups, rich metadata, each retrieval channel, RRF constant/depth, candidate `k`, exact/HNSW, thinking on/off, candidate order, hierarchy fields, confidence threshold.

### 12.4 Error taxonomy và statistics

Tag root cause: missed/spurious/boundary/type; assertion cue/scope/section; abbreviation/diacritic/unit; missing alias/index; gold outside top-k; parent-child; wrong ingredient/strength/form; unsupported specificity; stale/invalid ID; fail-to-abstain; gold/scorer ambiguity.

Final comparison dùng paired document/patient-cluster bootstrap (>=2000 replicates), 95% CI; McNemar cho paired correctness; randomization/bootstrap cho ranking/F1. Báo absolute delta, CI, sample count và correction (Holm cho confirmatory, Benjamini-Hochberg cho exploratory). Nguồn: [bootstrap](https://doi.org/10.1201/9780429246593), [NLP significance guide](https://aclanthology.org/P18-1128/), [IR tests](https://doi.org/10.1145/1321440.1321528).

## 13. Runtime Và Cách Chạy

### 13.1 Services

| Service | Device | Endpoint nội bộ | Model |
|---|---|---|---|
| `dev` | CPU | client | không load model |
| `llm-server` | NVIDIA GPU | `http://llm-server:8080/v1` | Qwen3.5-4B Q4_K_M |
| `embedding-server` | CPU | `http://embedding-server:8081/v1` | Qwen3-Embedding-0.6B Q8_0 |

Model tự tải qua `-hf` vào volume `model-cache`; `docker compose down` giữ cache, `docker compose down -v` xóa cache. Port không expose ra host. Xem toàn bộ flags trong [`docker-compose.yml`](docker-compose.yml) và llama.cpp [`server README`](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

### 13.2 Dev Container

1. Mở repo bằng VS Code.
2. `Ctrl+Shift+P` -> `Dev Containers: Rebuild and Reopen in Container` lần đầu.
3. Những lần sau dùng `Dev Containers: Reopen in Container`.
4. Dev container không tự start model để tránh download ngoài ý muốn.

### 13.3 Start và kiểm tra

```powershell
docker run --rm --gpus all nvidia/cuda:12.9.1-base-ubuntu24.04 nvidia-smi
docker compose up -d llm-server embedding-server
docker compose ps
```

```powershell
docker compose exec llm-server curl -sS -H "Authorization: Bearer local-internal-key" http://127.0.0.1:8080/v1/models
docker compose exec embedding-server curl -sS -H "Authorization: Bearer local-internal-key" -H "Content-Type: application/json" -d '{"model":"qwen3-embedding-0.6b","input":"Instruct: Retrieve an ICD-10 concept. Query: đau ngực"}' http://127.0.0.1:8081/v1/embeddings
docker compose logs llm-server
docker compose logs embedding-server
```

Do repo chưa có app/pipeline, hiện chưa có lệnh inference thật. Các CLI mục tiêu sau khi triển khai:

```text
python -m medical_ontology --text "..."
python -m medical_ontology --input note.txt --output note.json
python -m medical_ontology --input-dir test/input --output-dir output
python -m medical_ontology build-data
python -m medical_ontology build-index
python -m medical_ontology evaluate
python -m medical_ontology package --input-dir test/input --output-dir output
```

### 13.4 Resource policy 4 GB VRAM

- LLM `parallel=1`; embedding CPU; không load model per request.
- Nếu OOM: KV `q8_0 -> q4_0`; context `4096 -> 3072 -> 2048`; ubatch `64 -> 32`; batch `128 -> 64`; GPU layers `all -> auto/partial`.
- Tắt thinking cho extraction trước khi hạ model; chỉ bật cho ambiguous reranking nếu benchmark chứng minh lợi ích.
- Ghi GPU/CPU/RAM, image tag, model checksum, context/KV/batch/thinking trong mọi benchmark.

## 14. Cấu Trúc Code Đề Xuất

```text
src/medical_ontology/
├── cli.py                 entrypoint: build/infer/evaluate/package
├── contracts.py           exact BTC + rich internal dataclasses
├── data/                  acquisition, ICD/RxNorm parsers, aliases
├── extraction/            rules, LLM client, assertions, span alignment
├── retrieval/             exact, char TF-IDF, BM25, RRF, hybrid
├── indexing/              HNSW, persistence, manifests
├── mapping/               ICD/RxNorm constraints and confidence
├── pipeline/              batch orchestration and fallbacks
├── validation/            spans, ontology whitelist, output, ZIP
└── evaluation/            BTC proxy, NER, IR, calibration, benchmark

schemas/                   BTC, internal, artifact and evaluation schemas
prompts/                   versioned prompts + examples + manifest
data/raw/                  ignored authoritative artifacts
data/processed/            ignored generated corpora
data/eval/                 licensed/approved gold or local-only data
artifacts/                 embeddings, indexes, runs, reports
tests/{unit,integration,e2e,regression,contract}/
```

Artifact manifest phải lưu source/parser/alias/model/prompt/config/index/scorer versions và checksums. Index loader phải từ chối model/dimension/metric/data checksum mismatch.

## 15. Phân Công Và Tiến Độ

Tên thành viên:

- **Mạc Phúc Khang**
- **Dương Huệ Mẫn**
- **Võ Huỳnh Quốc Thái**
- **Nguyễn Hoàng Thái**
- **Lương Minh Quân**

### 15.1 Ownership

| Người | Accountable |
|---|---|
| Khang | Tech lead, contract/architecture, extraction design, reviews, integration, release/report/slides/video |
| Dương Huệ Mẫn | Official data, provenance/license, parser specification, ontology scope, alias/data QA |
| Võ Huỳnh Quốc Thái | Model clients, extraction implementation, dense/sparse/RRF, HNSW, retrieval benchmark |
| Nguyễn Hoàng Thái | QA plan, gold/fixtures, scorers, regression, error analysis, release verification |
| Lương Minh Quân | Package/config, parsers, CLI, orchestration, validators, batch ZIP, demo |

### 15.2 Critical-path tasks

| Ưu tiên | Deliverable | Owner | Reviewer | Dependency/acceptance |
|---:|---|---|---|---|
| P0 | Đề + output contract + scorer | Khang, Nguyễn Hoàng Thái | cả team | toy scorer đúng công thức BTC |
| P0 | ICD/RxNorm acquisition manifests | Dương Huệ Mẫn | Khang | URL, date, hash, license |
| P0 | ICD/RxNorm parsers | Lương Minh Quân, Dương Huệ Mẫn | QA | counts, schema, manual samples |
| P0 | Gold/dev/calibration split | Nguyễn Hoàng Thái | Dương Huệ Mẫn | no leakage, all types/assertions |
| P0 | Rules + exact/char/BM25 baseline | Võ Huỳnh Quốc Thái | Khang, QA | deterministic E2E |
| P0 | Qwen extraction + dense exact | Võ Huỳnh Quốc Thái, Khang | QA | valid spans, Recall@k |
| P0 | Code-level RRF + mapper | Võ Huỳnh Quốc Thái, Lương Minh Quân | Khang | whitelist-only candidates |
| P0 | Batch validator + ZIP | Lương Minh Quân | Nguyễn Hoàng Thái | exactly 100 valid files |
| P1 | HNSW implementation | Võ Huỳnh Quốc Thái | Khang | invariants + persistence |
| P1 | Exact-vs-HNSW benchmark | Nguyễn Hoàng Thái | Võ Huỳnh Quốc Thái | recall-latency-memory Pareto |
| P1 | Selective LLM reranker/calibration | Khang, Võ Huỳnh Quốc Thái | QA | beats RRF baseline |
| P1 | Release/report/demo | Khang, Lương Minh Quân | cả team | reproducible clean-machine run |

Quy tắc: task >4 giờ tách nhỏ; mọi task Done phải có PR/commit, test, metric/artifact hoặc quyết định được ghi lại. Jira là source of truth cho status; GitHub là source of truth cho code/review. Branch: `<type>/MOR-<id>-<description>`, PR: `[MOR-<id>] Title`, squash merge sau CI và review.

### 15.3 Milestones cần re-baseline

Lịch cũ trong Git history đặt code freeze `28/07/2026 23:00` và deliverables `02/08/2026`, nhưng đề gốc ghi vòng 1 kết thúc `30/07/2026`. Team phải xác nhận portal/BTC ngay và re-baseline Jira; không dùng mốc 02/08 cho submission vòng 1 nếu portal đóng 30/07.

Milestone kỹ thuật theo thứ tự:

1. Contract/scorer/data snapshot.
2. Deterministic E2E baseline.
3. Qwen extraction + dense exact + hybrid.
4. Frozen RC + 100-file packaging.
5. HNSW/reranker chỉ khi không đe dọa RC.
6. Report/demo/advanced experiments sau submission-safe baseline.

## 16. Definition Of Done

### Data

- [ ] Source authority/version/URL/date/hash/license đầy đủ.
- [ ] Parser deterministic, counts và issue log; manual double-check samples.
- [ ] Không trộn ICD-10-CM; không trộn RxNorm releases.
- [ ] Alias provenance/collision/review status đầy đủ.

### Pipeline

- [ ] `raw[start:end] == text` cho mọi entity.
- [ ] Đúng 5 type; assertions là array string đúng applicability.
- [ ] Candidate chỉ cho diagnosis/drug, thuộc pinned ontology.
- [ ] Rule-only fallback chạy được; invalid output không được ghi.
- [ ] Một command xử lý folder và tạo đúng 100 JSON + ZIP.

### Retrieval/HNSW

- [ ] Exact, char, BM25, dense và RRF có unit tests + benchmark.
- [ ] Alias collapsed về code trước RRF.
- [ ] HNSW degree/layer/entry/tie invariants và save/load tests pass.
- [ ] HNSW báo ANN recall so với exact, không chỉ clinical Recall@k.
- [ ] Index manifest chặn stale/incompatible artifacts.

### Evaluation/release

- [ ] Scorer toy/perfect/empty/wrong-type cases pass.
- [ ] Train/dev/calibration/test không leakage.
- [ ] Component + E2E + competition-proxy + efficiency metrics có version.
- [ ] Ablations và error analysis trước khi chọn model/config.
- [ ] Reproduce từ clean environment; không secret, PHI, raw licensed data hoặc model weight trong Git.
- [ ] README commands đã chạy thử, không quảng cáo placeholder là functional.

## 17. Troubleshooting

| Lỗi | Kiểm tra/xử lý |
|---|---|
| Docker không thấy GPU | Chạy NVIDIA CUDA `nvidia-smi` container; sửa host runtime trước |
| LLM OOM | Theo thứ tự KV/context/ubatch/batch/GPU layers tại Resource Policy |
| Download model lỗi | Start lại; cache nằm trong `model-cache`; chỉ `down -v` khi muốn xóa |
| App trong container gọi model lỗi | Dùng Docker DNS `llm-server`/`embedding-server`, không dùng localhost |
| Embedding dimension mismatch | Rebuild index đúng model/dim/metric/data checksum |
| Candidate hallucinated | Whitelist validator phải loại; LLM không được trực tiếp ghi code |
| RxNorm mapping quá cụ thể | Kiểm tra ingredient/strength/form/TTY; backoff hoặc abstain |
| ICD code giống ICD-10-CM | Kiểm tra source-system provenance; quarantine US-only code |
| HNSW recall thấp | So metric/normalization, heap/termination, pruning, `ef`, insertion order |
| Offset sai sau normalize | Không output offset trên normalized text; dùng immutable raw + offset map |
| Score local khác portal | Kiểm tra entity matching, WER tokenization, Jaccard empty cases và wrong-type rule |

## 18. Thư Viện Nghiên Cứu

### Competition, ontology và interoperability

- [Thông tư 06/2026/TT-BYT](https://chinhphu.vn/?docid=217536&pageid=27160)
- [WHO ICD classification](https://www.who.int/standards/classifications/classification-of-diseases)
- [WHO ICD-10 Browser](https://icd.who.int/browse10/2019/en)
- [NLM RxNorm overview](https://www.nlm.nih.gov/research/umls/rxnorm/index.html)
- [RxNorm files](https://www.nlm.nih.gov/research/umls/rxnorm/docs/rxnormfiles.html)
- [RxNorm technical docs](https://www.nlm.nih.gov/research/umls/rxnorm/docs/techdoc.html)
- [RxNav API](https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html)
- [UMLS reference manual](https://www.ncbi.nlm.nih.gov/books/NBK9676/)
- [HL7 FHIR terminology module](https://hl7.org/fhir/terminology-module.html), chỉ tham khảo modeling/interoperability; không thay competition schema

### Clinical NLP và normalization

- [NegEx](https://pubmed.ncbi.nlm.nih.gov/12123149/)
- [ConText](https://doi.org/10.1016/j.jbi.2009.05.002)
- [PhoNER_COVID19 paper](https://aclanthology.org/2021.naacl-main.173/)
- [BioSyn paper](https://aclanthology.org/2020.acl-main.335/) và [repo](https://github.com/dmis-lab/BioSyn)
- [SapBERT paper](https://aclanthology.org/2021.naacl-main.334/)
- [BERN2](https://github.com/dmis-lab/BERN2), kiến trúc tham khảo, không phù hợp resource hiện tại
- [MedMentions](https://huggingface.co/datasets/bigbio/medmentions), English control, không thay Vietnamese test

### Retrieval, ANN và models

- [Introduction to Information Retrieval](https://nlp.stanford.edu/IR-book/)
- [BM25 and Beyond](https://doi.org/10.1561/1500000019)
- [RRF paper](https://doi.org/10.1145/1571941.1572114)
- [DPR](https://arxiv.org/abs/2004.04906)
- [HNSW paper](https://arxiv.org/abs/1603.09320)
- [hnswlib](https://github.com/nmslib/hnswlib)
- [Faiss](https://github.com/facebookresearch/faiss), exact/ANN reference only nếu core yêu cầu tự code
- [ColBERT](https://arxiv.org/abs/2004.12832)
- [SPLADE](https://arxiv.org/abs/2107.05720)
- [Qwen3 Embedding](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B)
- [Qwen3 Reranker](https://huggingface.co/Qwen/Qwen3-Reranker-0.6B)
- [BGE-M3](https://huggingface.co/BAAI/bge-m3)
- [Sentence Transformers](https://www.sbert.net/), advanced training/evaluation reference

### Evaluation, calibration và reproducibility

- [NIST trec_eval](https://github.com/usnistgov/trec_eval)
- [ir_measures](https://ir-measur.es/)
- [ranx](https://github.com/AmenRa/ranx)
- [Calibration paper](https://proceedings.mlr.press/v70/guo17a.html)
- [Proper scoring rules](https://doi.org/10.1198/016214506000001437)
- [Selective classification](https://proceedings.neurips.cc/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Abstract.html)
- [Conformal prediction](https://arxiv.org/abs/2107.07511)
- [ML reproducibility checklist](https://www.cs.mcgill.ca/~jpineau/ReproducibilityChecklist.pdf)
- [Model Cards](https://arxiv.org/abs/1810.03993) và [Datasheets for Datasets](https://arxiv.org/abs/1803.09010)

### Runtime và engineering

- [llama.cpp](https://github.com/ggml-org/llama.cpp)
- [llama.cpp HTTP server](https://github.com/ggml-org/llama.cpp/tree/master/tools/server)
- [GGUF specification/code](https://github.com/ggml-org/ggml/blob/master/docs/gguf.md)
- [Docker Compose](https://docs.docker.com/compose/)
- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
- [pytest](https://docs.pytest.org/)
- [Ruff](https://docs.astral.sh/ruff/)
- [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow)
- [Protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)

## License Và Citation

Code do nhóm viết dùng MIT License. Đề thi, ICD-10, RxNorm, datasets, model weights và tài liệu bên thứ ba giữ nguyên license/terms của chủ sở hữu. Luôn cite paper/model/data đã dùng, ghi version và access date; không hiểu MIT của repository là quyền tái phân phối các artifact bên thứ ba.
