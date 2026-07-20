import pytest
import numpy as np
import os


class TestHNSW:
    
    
    # ==========================================
    # 1. Cosine Metric & Vector Constraints
    # ==========================================


    """Test 1: Vector gồm các số 0 phải bị từ chối vì không thể chuẩn hóa L2 (Cosine Distance)."""

    def test_add_zero_vector(self, hnsw_db, vector_dim):
        
        zero_vector = np.zeros(vector_dim, dtype = np.float32)
        
        try:
            hnsw_db.add(zero_vector, {"id": "zero_doc"})
            
            # Nếu hàm add chấp nhận vector 0 mà không báo lỗi, test fail và báo lỗi
            pytest.fail("Lỗi Validation: Hệ thống đã cho phép chèn Zero Vector! Điều này sẽ làm hỏng thuật toán vì phép tính Cosine Distance sẽ bị lỗi ZeroDivsionError.")
            
        except ValueError:
            pass


    """Test 2: Không được thêm duplicate vector trong đồ thị """
    def test_add_duplicate_vector(self, hnsw_db, sample_vector):

        hnsw_db.add(sample_vector, {"id": "doc_1"})
        
        try:
            hnsw_db.add(sample_vector, {"id": "doc_2"})
            
            # Nếu tiếp tục chèn thành công vector trùng lặp, test sẽ Fail
            pytest.fail("Lỗi Duplicate: Hệ thống cho phép thêm vector đã tồn tại")
            
        except ValueError:
            pass


    # ==========================================
    # 2. HNSW Graph Invariants 
    # ==========================================


    """Test 3: Node đầu tiên được chèn vào phải trở thành Entry Point và nằm ở Max Layer."""
    def test_entry_point_initialization(self, hnsw_db, sample_vector):

        assert hnsw_db.get_size() == 0, "Trạng thái khởi tạo lỗi: Cơ sở dữ liệu HNSW rỗng."
        
        hnsw_db.add(sample_vector, {"id": "first_node"})
        
        entry_point_id = hnsw_db.get_entry_point()
        assert entry_point_id == "first_node", "Khởi tạo sai: Node đầu tiên không được gán làm Entry Point."
        
        # Node đầu tiên phải quyết định max level hiện tại của đồ thị
        assert hnsw_db.get_max_level() == hnsw_db.get_node_level("first_node"), "Invariant lỗi: Max level của đồ thị phải bằng đúng level của node đầu tiên."


    """Test 4: Nếu node có level L, nó bắt buộc phải tồn tại ở mọi layer từ 0 đến L."""
    def test_layer_existence_invariant(self, hnsw_db, vector_dim):

        # Chèn một số node để tạo layer
        for i in range(10):
            vec = np.random.rand(vector_dim).astype(np.float32)
            hnsw_db.add(vec, {"id": f"node_{i}"})
        
        # Lấy entry point (là node level cao nhất)
        ep_id = hnsw_db.get_entry_point()
        ep_level = hnsw_db.get_node_level(ep_id)
        
        # Kiểm tra sự tồn tại ở tất cả các layer
        for level in range(ep_level + 1):
            assert ep_id in hnsw_db.get_nodes_at_level(level), f"Node {ep_id} bị thiếu ở layer {level}"


    """Test 5: Bậc (degree) của node tại layer 0 phải <= M0, tại layer > 0 phải <= M."""
    def test_degree_limits_m_and_m0(self, hnsw_db, vector_dim):
        # M là maximum degree (layer > 0), M0 là maximum degree ở level 0
        M = hnsw_db.get_m()
        M0 = hnsw_db.get_m0()
        
        # Chèn số lượng node đủ lớn để đồ thị hình thành các kết nối phức tạp 
        for i in range(50):
            vec = np.random.rand(vector_dim).astype(np.float32)
            hnsw_db.add(vec, {"id": f"node_{i}"})
            
        for i in range(50):
            node_id = f"node_{i}"
            node_level = hnsw_db.get_node_level(node_id)
            
            for level in range(node_level + 1):
                neighbors = hnsw_db.get_neighbors(node_id, level)
                if level == 0:
                    assert len(neighbors) <= M0, f"Layer 0 vi phạm giới hạn M0 ({len(neighbors)} > {M0})"
                else:
                    assert len(neighbors) <= M, f"Layer {level} vi phạm giới hạn M ({len(neighbors)} > {M})"


    """Test 6: Đảm bảo adjacency list không chứa chính nó (No self-loop)."""
    def test_no_self_loops(self, hnsw_db, vector_dim):

        for i in range(10):
            vec = np.random.rand(vector_dim).astype(np.float32)
            hnsw_db.add(vec, {"id": f"node_{i}"})
            
        for i in range(10):
            node_id = f"node_{i}"
            node_level = hnsw_db.get_node_level(node_id)
            for level in range(node_level + 1):
                neighbors = hnsw_db.get_neighbors(node_id, level)
                assert node_id not in neighbors, f"Phát hiện self-loop tại node {node_id}"

    # ==========================================
    # 3. Add Validations & State Persistence (Viết lại)
    # ==========================================

    """Test 7: Kiểm tra hàm add có thực sự lưu metadata vào bộ nhớ hay không"""
    def test_add_stores_metadata_and_increases_size(self, hnsw_db, sample_vector, sample_metadata):
        
        # Gắn thêm ID vào metadata để lưu trữ
        sample_metadata["id"] = "test_meta_doc"
        
        initial_size = hnsw_db.get_size()
        hnsw_db.add(sample_vector, sample_metadata)
        
        # 1. Size phải tăng lên 1
        assert hnsw_db.get_size() == initial_size + 1, f"Lỗi trạng thái: Sau khi add, kích thước DB không tăng. (Kỳ vọng: {initial_size + 1}, Thực tế: {hnsw_db.get_size()})"
        
        # 2. Lấy metadata bằng hàm getter từ vectorbase để đối chiếu
        # Giả định rằng vectorbase có hàm getter
        stored_meta = hnsw_db.get_metadata("test_meta_doc")
        
        assert stored_meta is not None, "Lỗi lưu trữ: không lấy được vector, hàm get_metadata trả về None."
        
        assert stored_meta["text"] == sample_metadata["text"], "Lỗi toàn vẹn dữ liệu: Text của Metadata bị thay đổi sau khi lưu vào Vectorbase."


    """Test 8: Hàm add bắt buộc phải từ chối vector có số chiều (dimension) không khớp với cấu hình ban đầu."""
    def test_add_dimension_mismatch(self, hnsw_db, vector_dim):
        
        # Cố tình tạo ra một vector dư 1 chiều
        wrong_dim_vector = np.random.rand(vector_dim + 1).astype(np.float32)
        
        try:
            hnsw_db.add(wrong_dim_vector, {"id": "wrong_dim_doc"})
            
            # Nếu hệ thống chấp nhận vector sai số chiều, test fail 
            pytest.fail(f"Lỗi Validation: Hệ thống đã cho phép chèn vector có số chiều ({vector_dim + 1}) khác với chuẩn của DB ({vector_dim}).")
            
        except ValueError:
            pass


    """Test 9: Hàm add bắt buộc phải từ chối kiểu dữ liệu không phải là Float32 (để tối ưu Cosine Distance)."""
    def test_add_invalid_datatype(self, hnsw_db, vector_dim):
        
        # Cố tình ép kiểu float64 
        invalid_type_vector = np.random.rand(vector_dim).astype(np.float64)
        
        try:
            hnsw_db.add(invalid_type_vector, {"id": "wrong_type_doc"})
            
            pytest.fail("Lỗi Validation Type: Hệ thống cho phép chèn vector có data type không hợp lệ.")
            
        except (ValueError, TypeError):
            pass


    """Test 10: Connectivity Invariant - Node thứ 2 trở đi thêm vào bắt buộc phải có ít nhất 1 neighbor ở Layer 0."""
    def test_add_ensures_connectivity_at_layer_zero(self, hnsw_db, vector_dim):
        
        vec1 = np.random.rand(vector_dim).astype(np.float32)
        vec2 = np.random.rand(vector_dim).astype(np.float32)
        
        hnsw_db.add(vec1, {"id": "node_1"}) # Node đầu tiên trở thành entry point 
        hnsw_db.add(vec2, {"id": "node_2"}) # Node thứ 2 được chèn vào
        
        # Node thứ 2 bắt buộc phải nối với node 1 ở Layer 0
        neighbors = hnsw_db.get_neighbors("node_2", level = 0)
        
        assert len(neighbors) > 0, "Graph Invariant không hợp lệ: Node vừa được add vào không có bất kỳ cạnh nối nào với các node trước đó ở Layer 0."
        assert "node_1" in neighbors, "Lỗi thuật toán kết nối: Đồ thị chỉ có 2 node, nhưng hàm add không tạo cạnh nối giữa node_2 và node_1."