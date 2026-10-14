import numpy as np

def convolve2d(img, kernel):
    """
    Tích chập 2D cơ bản (tự cài đặt theo kiến thức Phần A).
    img: mảng 2D float hoặc int
    kernel: mảng 2D (khuyên dùng kích thước lẻ kh x kw)
    """
    img = np.asarray(img, dtype=np.float64)
    kernel = np.asarray(kernel, dtype=np.float64)
    
    kh, kw = kernel.shape
    pad_h = kh // 2
    pad_w = kw // 2
    
    # Đệm viền phản xạ (reflect) để giữ nguyên kích thước ảnh
    padded = np.pad(img, ((pad_h, pad_h), (pad_w, pad_w)), mode='reflect')
    
    # Lật nhân tích chập theo đúng định nghĩa toán học
    k_flipped = np.flipud(np.fliplr(kernel))
    
    h, w = img.shape
    out = np.zeros((h, w), dtype=np.float64)
    
    # Tích chập cục bộ
    for i in range(kh):
        for j in range(kw):
            out += k_flipped[i, j] * padded[i:i + h, j:j + w]
            
    return out

def get_gaussian_kernel(size=5, sigma=1.0):
    """
    Tạo nhân Gauss 2D kích thước size x size với độ lệch chuẩn sigma.
    """
    if size % 2 == 0:
        size += 1
    r = size // 2
    y, x = np.ogrid[-r:r+1, -r:r+1]
    k = np.exp(-(x**2 + y**2) / (2.0 * sigma**2))
    k_sum = k.sum()
    if k_sum > 0:
        k = k / k_sum
    return k
