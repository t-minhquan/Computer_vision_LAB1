import numpy as np

def integral_image(img):
    """
    Tạo ảnh tích phân (summed-area table) S.
    img: mảng (H, W) uint8 hoặc số thực.
    Trả về S kích thước (H+1, W+1), dtype int64, hàng 0 và cột 0 bằng 0.
    """
    h, w = img.shape
    # Bắt buộc ép kiểu int64 trước khi tích lũy để tránh tràn số (overflow)
    img_64 = np.asarray(img, dtype=np.int64)
    
    # Tạo mảng đệm (H+1, W+1) với hàng 0 và cột 0 toàn 0
    s = np.zeros((h + 1, w + 1), dtype=np.int64)
    
    # Tính tích lũy dọc trục hàng rồi trục cột
    s[1:, 1:] = np.cumsum(np.cumsum(img_64, axis=0), axis=1)
    return s

def box_sum(S, y1, x1, y2, x2):
    """
    Tính tổng các điểm ảnh trong vùng chữ nhật [y1..y2, x1..x2] (bao gồm cả 2 biên).
    Hỗ trợ vector hóa khi y1, x1, y2, x2 là các mảng numpy 2 chiều.
    """
    # Vì S có đệm 0 ở vị trí hàng 0, cột 0 nên:
    # Điểm đáy-phải (y2, x2) trên ảnh gốc ứng với (y2+1, x2+1) trên S
    # Điểm trên-trái (y1, x1) trừ đi 1 ứng với chỉ số (y1, x1) trên S
    # Công thức: D - B - C + A
    d = S[y2 + 1, x2 + 1]
    b = S[y1, x2 + 1]
    c = S[y2 + 1, x1]
    a = S[y1, x1]
    return d - b - c + a

def local_mean_std(img, radius):
    """
    Tính kỳ vọng (mean) và độ lệch chuẩn (std) cục bộ trong cửa sổ bán kính radius.
    Cửa sổ có kích thước (2*radius + 1) x (2*radius + 1), tự động xử lý biên ảnh.
    Trả về: (mean, std), mỗi mảng có kích thước (H, W) kiểu float64.
    """
    h, w = img.shape
    img_float = img.astype(np.float64)
    
    # 1. Dựng 2 ảnh tích phân: S1 cho ảnh gốc, S2 cho bình phương ảnh gốc
    s1 = integral_image(img_float)
    s2 = integral_image(img_float ** 2)
    
    # 2. Xác định tọa độ hộp chữ nhật lân cận cho mọi điểm ảnh (vectorized)
    y_idx, x_idx = np.indices((h, w))
    y1 = np.maximum(y_idx - radius, 0)
    y2 = np.minimum(y_idx + radius, h - 1)
    x1 = np.maximum(x_idx - radius, 0)
    x2 = np.minimum(x_idx + radius, w - 1)
    
    # 3. Diện tích cửa sổ thực tế (tự co lại ở mép biên)
    count = (y2 - y1 + 1) * (x2 - x1 + 1)
    
    # 4. Tính tổng I và tổng I^2 trong O(1)
    sum1 = box_sum(s1, y1, x1, y2, x2)
    sum2 = box_sum(s2, y1, x1, y2, x2)
    
    mean = sum1 / count
    
    # 5. Phương sai = E[X^2] - (E[X])^2
    var = (sum2 / count) - (mean ** 2)
    
    # CỰC KỲ QUAN TRỌNG: Kẹp phương sai không âm để tránh số âm cực nhỏ do sai số float64 sinh ra NaN
    var = np.maximum(var, 0.0)
    std = np.sqrt(var)
    
    return mean, std

def adaptive_threshold(img, radius=15, method='bradley', t=0.15, k=0.34):
    """
    Phân ngưỡng thích nghi cục bộ dùng ảnh tích phân.
    img: mảng (H, W) uint8
    radius: bán kính lân cận (kích thước cửa sổ là 2*radius + 1)
    method: 'bradley' hoặc 'sauvola'
    t: hệ số lệch cho Bradley-Roth (mặc định 0.15)
    k: hệ số tương phản cho Sauvola (mặc định 0.34)
    Trả về: ảnh nhị phân (H, W) uint8 với giá trị 0 hoặc 255.
    """
    img = np.asarray(img, dtype=np.uint8)
    
    if method.lower() == 'bradley':
        # Bradley-Roth chỉ cần tính mean
        s1 = integral_image(img)
        h, w = img.shape
        y_idx, x_idx = np.indices((h, w))
        y1 = np.maximum(y_idx - radius, 0)
        y2 = np.minimum(y_idx + radius, h - 1)
        x1 = np.maximum(x_idx - radius, 0)
        x2 = np.minimum(x_idx + radius, w - 1)
        
        count = (y2 - y1 + 1) * (x2 - x1 + 1)
        sum1 = box_sum(s1, y1, x1, y2, x2)
        mean = sum1 / count
        
        # Ngưỡng T = mean * (1 - t)
        thresh = mean * (1.0 - t)
        
    elif method.lower() == 'sauvola':
        # Sauvola kết hợp mean và std
        mean, std = local_mean_std(img, radius)
        # R = 128 đối với ảnh xám 8-bit
        thresh = mean * (1.0 + k * ((std / 128.0) - 1.0))
    else:
        raise ValueError(f"Phương thức không hỗ trợ: {method}")
        
    # Điểm ảnh tối hơn ngưỡng được coi là đối tượng/tiền cảnh (foreground = 255)
    bin_img = np.where(img < thresh, 255, 0).astype(np.uint8)
    return bin_img
