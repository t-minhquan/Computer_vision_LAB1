import numpy as np

def clip_histogram(hist, clip_limit):
    """
    Cắt và phân phối lại lược đồ.
    hist: mảng (L,) số nguyên (thường L = 256).
    clip_limit: ngưỡng cắt tối đa cho mỗi bin.
    Trả về mảng (L,) đã cắt, bảo toàn chính xác tổng số điểm ảnh.
    """
    hist = hist.astype(np.int64)
    if clip_limit is None or clip_limit <= 0:
        return hist
    
    # 1. Tìm các cột vượt ngưỡng và cắt bớt
    excess = 0
    clipped = hist.copy()
    mask = clipped > clip_limit
    excess = np.sum(clipped[mask] - clip_limit)
    clipped[mask] = clip_limit
    
    # 2. Phân phối đều phần dư E cho toàn bộ 256 mức
    num_bins = len(hist)
    bonus = excess // num_bins
    clipped += bonus
    
    # 3. Phần dư còn sót lại (excess % num_bins) chia đều cho các bin đầu
    leftover = excess % num_bins
    if leftover > 0:
        clipped[:leftover] += 1
        
    return clipped

def build_tile_luts(img, grid=(8, 8), clip_limit=2.0):
    """
    Chia ảnh thành Gy x Gx ô, tính lược đồ, cắt gọt và dựng bảng tra LUT cho từng ô.
    img: mảng (H, W) uint8
    grid: tuple (Gy, Gx) số lượng ô theo chiều dọc và ngang
    clip_limit: hệ số cắt (so với chiều cao trung bình của mỗi bin trong ô)
    Trả về: mảng (Gy, Gx, 256) uint8 chứa LUT của từng ô.
    """
    h, w = img.shape
    gy, gx = grid
    
    tile_h = h / gy
    tile_w = w / gx
    
    luts = np.zeros((gy, gx, 256), dtype=np.uint8)
    
    for i in range(gy):
        y0 = int(round(i * tile_h))
        y1 = int(round((i + 1) * tile_h))
        for j in range(gx):
            x0 = int(round(j * tile_w))
            x1 = int(round((j + 1) * tile_w))
            
            # Cắt ảnh của ô hiện tại
            tile = img[y0:y1, x0:x1]
            n_tile = tile.size
            if n_tile == 0:
                luts[i, j] = np.arange(256, dtype=np.uint8)
                continue
                
            # Đếm lược đồ xám
            hist = np.bincount(tile.ravel(), minlength=256)
            
            # Ngưỡng cắt thực tế dựa trên số điểm ảnh của ô và clip_limit
            # Nếu clip_limit là tỉ lệ s_max thì limit = clip_limit * (n_tile / 256)
            actual_limit = int(clip_limit * (n_tile / 256.0))
            if actual_limit < 1:
                actual_limit = 1
                
            clipped_hist = clip_histogram(hist, actual_limit)
            
            # Tính hàm phân phối tích lũy CDF và tạo LUT
            cdf = np.cumsum(clipped_hist)
            # Chuẩn hóa về dải [0, 255]
            lut = np.round(255.0 * cdf / cdf[-1]).astype(np.uint8)
            luts[i, j] = lut
            
    return luts

def clahe(img, grid=(8, 8), clip_limit=2.0):
    """
    CLAHE đầy đủ: cân bằng lược đồ xám thích nghi có giới hạn tương phản.
    Nội suy trực tiếp 4 giá trị vô hướng trong bảng tra LUT tại mỗi điểm ảnh.
    img: (H, W) uint8
    grid: (Gy, Gx)
    clip_limit: hệ số cắt
    Trả về: (H, W) uint8
    """
    img = np.asarray(img, dtype=np.uint8)
    h, w = img.shape
    gy, gx = grid
    
    # 1. Dựng LUT cho từng ô
    luts = build_tile_luts(img, grid=grid, clip_limit=clip_limit)
    
    # 2. Tính tọa độ tâm của các ô
    tile_h = h / gy
    tile_w = w / gx
    
    out = np.zeros((h, w), dtype=np.uint8)
    
    # Tạo lưới tọa độ điểm ảnh
    y_coords, x_coords = np.indices((h, w))
    
    # Tọa độ liên tục theo đơn vị ô tính từ tâm ô đầu tiên (0.5 * tile)
    # y = (i + 0.5) * tile_h => i_cont = (y - 0.5 * tile_h) / tile_h = y / tile_h - 0.5
    y_norm = y_coords / tile_h - 0.5
    x_norm = x_coords / tile_w - 0.5
    
    # Tìm chỉ số ô xung quanh
    i0 = np.floor(y_norm).astype(np.int32)
    j0 = np.floor(x_norm).astype(np.int32)
    i1 = i0 + 1
    j1 = j0 + 1
    
    # Trọng số nội suy a (chiều x/cột), b (chiều y/hàng)
    b = y_norm - i0
    a = x_norm - j0
    
    # Kẹp chỉ số về biên hợp lệ để tự động xử lý góc và cạnh mà không cần if-else
    i0_clamped = np.clip(i0, 0, gy - 1)
    i1_clamped = np.clip(i1, 0, gy - 1)
    j0_clamped = np.clip(j0, 0, gx - 1)
    j1_clamped = np.clip(j1, 0, gx - 1)
    
    # Kẹp trọng số a, b về [0, 1] cho các vùng ngoài biên
    a = np.clip(a, 0.0, 1.0)
    b = np.clip(b, 0.0, 1.0)
    
    # Giá trị mức xám tại từng điểm
    v = img
    
    # Tra cứu trực tiếp giá trị LUT vô hướng của 4 tâm lân cận
    t00 = luts[i0_clamped, j0_clamped, v]
    t01 = luts[i0_clamped, j1_clamped, v]
    t10 = luts[i1_clamped, j0_clamped, v]
    t11 = luts[i1_clamped, j1_clamped, v]
    
    # Nội suy song tuyến theo công thức (4) trong tài liệu
    # I_out = (1-b) * [(1-a)*T00 + a*T01] + b * [(1-a)*T10 + a*T11]
    top = (1.0 - a) * t00 + a * t01
    bot = (1.0 - a) * t10 + a * t11
    res = (1.0 - b) * top + b * bot
    
    out = np.round(np.clip(res, 0, 255)).astype(np.uint8)
    return out
