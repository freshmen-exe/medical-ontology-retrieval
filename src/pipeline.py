#!/usr/bin/env python3
import json
import os
import re
from typing import Any

import requests


class LLMClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None, model: str | None = None) -> None:
        self.base_url = base_url or os.environ.get("LLM_BASE_URL", "http://localhost:8080/v1")
        self.api_key = api_key or os.environ.get("LLM_API_KEY", "local-internal-key")
        self.model = model or os.environ.get("LLM_MODEL", "medical-extractor")

    def extract(self, text: str) -> list[dict[str, Any]]:
        """Gọi LLM trích xuất thô thực thể y khoa."""
        prompt = (
            "Trích xuất tất cả các thực thể y khoa từ đoạn văn bản y khoa sau đây.\n"
            "Các nhãn thực thể hợp lệ bao gồm:\n"
            "- TRIỆU_CHỨNG: Triệu chứng lâm sàng.\n"
            "- TÊN_XÉT_NGHIỆM: Tên các xét nghiệm hoặc thủ thuật.\n"
            "- KẾT_QUẢ_XÉT_NGHIỆM: Kết quả cụ thể của xét nghiệm (bao gồm trị số và đơn vị).\n"
            "- CHẨN_ĐOÁN: Bệnh lý hoặc chẩn đoán lâm sàng.\n"
            "- THUỐC: Tên thuốc hoặc dược chất.\n\n"
            "Với mỗi thực thể, xác định các cờ ngữ cảnh (assertions): isNegated (bị phủ định), "
            "isFamily (tiền sử gia đình), isHistorical (tiền sử bản thân/quá khứ).\n"
            "Chỉ trả về danh sách JSON đúng định dạng sau:\n"
            "[\n"
            "  {\n"
            '    "text": "tên thực thể nguyên văn",\n'
            '    "type": "NHÃN",\n'
            '    "assertions": {\n'
            '      "isNegated": true/false,\n'
            '      "isFamily": true/false,\n'
            '      "isHistorical": true/false\n'
            "    }\n"
            "  }\n"
            "]\n\n"
            f"Văn bản: {text}"
        )

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a professional medical assistant designed to output JSON list of clinical entities.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.1,
                "response_format": {"type": "json_object"},
            }
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=15,
            )
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                # Lọc hoặc parse JSON từ content
                parsed = json.loads(content)
                if isinstance(parsed, dict) and "entities" in parsed:
                    return parsed["entities"]
                if isinstance(parsed, list):
                    return parsed
            return []
        except Exception:
            # Fallback mock data khi không gọi được LLM Server
            return self._mock_fallback_extract(text)

    def validate(self, entity_text: str, entity_type: str, candidates: list[dict[str, Any]]) -> list[str]:
        """Gọi LLM lần 2 để lựa chọn mã chuẩn xác nhất."""
        if not candidates:
            return []

        prompt = (
            f"Dựa trên thực thể '{entity_text}' loại '{entity_type}', "
            "hãy chọn ra các mã chuẩn y khoa khớp nhất từ danh sách ứng viên sau.\n"
            'Đầu ra chỉ trả về mảng JSON chứa các mã được chọn (ví dụ: ["K21.9"]).\n'
            f"Danh sách ứng viên: {json.dumps(candidates, ensure_ascii=False)}"
        )
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a professional medical coding expert. Output a JSON list of strings representing the selected codes.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.1,
            }
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=10,
            )
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                # Trích xuất mảng JSON từ text
                match = re.search(r"\[.*\]", content, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
            return [candidates[0]["code"]]
        except Exception:
            return [candidates[0]["code"]]

    def _mock_fallback_extract(self, text: str) -> list[dict[str, Any]]:
        # Tìm kiếm regex thô để giả lập trích xuất
        mock_entities = []

        # Một số từ khóa tiếng Việt cơ bản để mock
        symptoms = ["ho khan", "sốt cao", "khó thở", "đau ngực", "mệt mỏi", "tiêu chảy"]
        drugs = ["Paracetamol", "Amoxicillin", "Ibuprofen", "Aspirin", "Metformin"]
        diagnoses = [
            "trào ngược dạ dày",
            "viêm thực quản",
            "tăng huyết áp",
            "đái tháo đường",
            "viêm dạ dày",
        ]

        lower_text = text.lower()

        for sym in symptoms:
            if sym in lower_text:
                idx = lower_text.find(sym)
                # Giữ nguyên hoa/thường từ text gốc
                original_chunk = text[idx : idx + len(sym)]
                mock_entities.append(
                    {
                        "text": original_chunk,
                        "type": "TRIỆU_CHỨNG",
                        "assertions": {
                            "isNegated": "không" in lower_text[:idx],
                            "isFamily": "mẹ" in lower_text or "bố" in lower_text,
                            "isHistorical": "tiền sử" in lower_text,
                        },
                    },
                )

        for dg in diagnoses:
            if dg in lower_text:
                idx = lower_text.find(dg)
                original_chunk = text[idx : idx + len(dg)]
                mock_entities.append(
                    {
                        "text": original_chunk,
                        "type": "CHẨN_ĐOÁN",
                        "assertions": {
                            "isNegated": "không" in lower_text[:idx],
                            "isFamily": "mẹ" in lower_text or "bố" in lower_text,
                            "isHistorical": "tiền sử" in lower_text,
                        },
                    },
                )

        for dr in drugs:
            if dr.lower() in lower_text:
                idx = lower_text.find(dr.lower())
                original_chunk = text[idx : idx + len(dr)]
                mock_entities.append(
                    {
                        "text": original_chunk,
                        "type": "THUỐC",
                        "assertions": {
                            "isNegated": False,
                            "isFamily": False,
                            "isHistorical": False,
                        },
                    },
                )

        return mock_entities


class MedicalPipeline:
    def __init__(self, llm_client: Any = None, vector_db: Any = None) -> None:
        """Khởi tạo Pipeline xử lý văn bản y khoa."""
        self.llm_client = llm_client or LLMClient()
        self.vector_db = vector_db

    def extract_entities_raw(self, text: str) -> list[dict[str, Any]]:
        """Bước 1: Trích xuất thực thể thô bằng LLM."""
        return self.llm_client.extract(text)

    def calculate_positions(self, original_text: str, entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Bước 2: Tính toán chính xác vị trí [l, r) của các cụm từ trong văn bản gốc.
        Sử dụng cơ chế tìm kiếm tuần tự và hỗ trợ tìm kiếm không phân biệt hoa thường làm fallback.
        """
        processed_entities = []
        last_index = 0

        for entity in entities:
            entity_text = entity.get("text", "")
            if not entity_text:
                continue

            # 1. Thử tìm kiếm phân biệt hoa thường bắt đầu từ last_index
            idx = original_text.find(entity_text, last_index)

            # 2. Fallback: Thử tìm kiếm từ đầu văn bản
            if idx == -1:
                idx = original_text.find(entity_text)

            # 3. Fallback 2: Thử tìm kiếm không phân biệt hoa thường
            if idx == -1:
                idx = original_text.lower().find(entity_text.lower(), last_index)
                if idx == -1:
                    idx = original_text.lower().find(entity_text.lower())
                if idx != -1:
                    # Cập nhật lại text của entity theo đúng văn bản gốc để thỏa mãn raw_text[l:r] == text
                    entity_text = original_text[idx : idx + len(entity_text)]

            if idx != -1:
                start_idx = idx
                end_idx = idx + len(entity_text)
                last_index = end_idx

                new_entity = entity.copy()
                new_entity["text"] = entity_text
                new_entity["position"] = [start_idx, end_idx]
                processed_entities.append(new_entity)
            else:
                new_entity = entity.copy()
                new_entity["position"] = []
                processed_entities.append(new_entity)

        return processed_entities

    def query_vector_db(self, entity_text: str, entity_type: str, n_results: int = 5) -> list[dict[str, Any]]:
        """Bước 3: Gọi truy vấn vào VectorDB."""
        if self.vector_db:
            return self.vector_db.query(query_text=entity_text, entity_type=entity_type, n_results=n_results)

        # Mockup database ứng viên dựa trên thực thể y tế
        if entity_type == "CHẨN_ĐOÁN":
            if "trào ngược" in entity_text.lower():
                return [
                    {
                        "code": "K21.9",
                        "name": "Bệnh trào ngược dạ dày-thực quản không viêm thực quản",
                    },
                    {
                        "code": "K21.0",
                        "name": "Bệnh trào ngược dạ dày-thực quản có viêm thực quản",
                    },
                    {"code": "K21", "name": "Bệnh trào ngược dạ dày - thực quản"},
                ][:n_results]
            if "huyết áp" in entity_text.lower():
                return [
                    {"code": "I10", "name": "Tăng huyết áp vô căn (nguyên phát)"},
                    {"code": "I15", "name": "Tăng huyết áp thứ phát"},
                ][:n_results]
        elif entity_type == "THUỐC" and "paracetamol" in entity_text.lower():
            return [
                {"code": "RX123", "name": "Paracetamol 500mg Oral Tablet"},
                {"code": "RX456", "name": "Paracetamol 250mg Oral Tablet"},
                {"code": "RX789", "name": "Paracetamol 100mg/ml Oral Solution"},
            ][:n_results]
        return []

    def reciprocal_rank_fusion(
        self,
        dense_results: list[dict[str, Any]],
        sparse_results: list[dict[str, Any]],
        rrf_k: int = 60,
    ) -> list[dict[str, Any]]:
        """Xếp hạng ứng viên bằng thuật toán Reciprocal Rank Fusion (RRF) kết hợp dense và sparse."""
        # Collapse alias by code đầu tiên
        dense_ranked = []
        seen_dense = set()
        for item in dense_results:
            code = item.get("code")
            if code and code not in seen_dense:
                seen_dense.add(code)
                dense_ranked.append(code)

        sparse_ranked = []
        seen_sparse = set()
        for item in sparse_results:
            code = item.get("code")
            if code and code not in seen_sparse:
                seen_sparse.add(code)
                sparse_ranked.append(code)

        rrf_scores = {}
        # Tính toán RRF đóng góp từ Dense
        for rank, code in enumerate(dense_ranked, 1):
            rrf_scores[code] = rrf_scores.get(code, 0.0) + 1.0 / (rrf_k + rank)

        # Tính toán RRF đóng góp từ Sparse
        for rank, code in enumerate(sparse_ranked, 1):
            rrf_scores[code] = rrf_scores.get(code, 0.0) + 1.0 / (rrf_k + rank)

        # Sắp xếp theo score RRF giảm dần, tie-break bằng code theo bảng chữ cái
        sorted_codes = sorted(rrf_scores.keys(), key=lambda x: (-rrf_scores[x], x))

        return [{"code": code, "rrf_score": rrf_scores[code]} for code in sorted_codes]

    def validate_candidates(self, entity_text: str, entity_type: str, candidates: list[dict[str, Any]]) -> list[str]:
        """Bước 4: Gọi LLM validator chọn mã chuẩn xác sau cùng."""
        if not candidates:
            return []
        return self.llm_client.validate(entity_text, entity_type, candidates)

    def run_pipeline(self, text: str) -> list[dict[str, Any]]:
        """Chạy toàn bộ pipeline xử lý văn bản y khoa."""
        # 1. Trích xuất thực thể thô
        raw_entities = self.extract_entities_raw(text)

        # 2. Tính toán vị trí [l, r)
        positioned_entities = self.calculate_positions(text, raw_entities)

        # 3. Chuẩn hóa và map mã
        final_entities = []
        for entity in positioned_entities:
            entity_type = entity.get("type", "")
            entity_text = entity.get("text", "")

            # Chuẩn hóa Assertions sang mảng chuỗi theo luật BTC
            raw_assertions = entity.get("assertions", {})
            assertions_list = []
            if isinstance(raw_assertions, dict):
                if raw_assertions.get("isNegated"):
                    assertions_list.append("isNegated")
                if raw_assertions.get("isFamily"):
                    assertions_list.append("isFamily")
                if raw_assertions.get("isHistorical"):
                    assertions_list.append("isHistorical")
            elif isinstance(raw_assertions, list):
                assertions_list = raw_assertions

            entity["assertions"] = assertions_list
            entity["candidates"] = []

            # Map code chỉ cho CHẨN_ĐOÁN và THUỐC
            # Sửa tên nhãn cho đồng bộ (hỗ trợ dấu gạch dưới hoặc không gạch dưới)
            clean_type = entity_type.replace(" ", "_")
            entity["type"] = clean_type

            if clean_type in {"CHẨN_ĐOÁN", "THUỐC"}:
                # Giả lập truy vấn từ Dense và Sparse (trong baseline, ta truy vấn qua DB mẫu)
                candidates_dense = self.query_vector_db(entity_text, clean_type, n_results=5)
                # Giả lập sparse kết quả (cho mục đích test RRF, ta lấy danh sách đảo ngược hoặc dịch chuyển)
                candidates_sparse = list(reversed(candidates_dense))

                # Thực hiện RRF fusion
                fused_candidates = self.reciprocal_rank_fusion(candidates_dense, candidates_sparse)

                # Gọi Validator để đưa ra mã cuối
                validated_codes = self.validate_candidates(entity_text, clean_type, fused_candidates)
                entity["candidates"] = validated_codes

            final_entities.append(entity)

        return final_entities
