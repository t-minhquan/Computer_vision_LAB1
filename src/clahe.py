import numpy as np


def clip_histogram(hist, clip_limit):
    """
    Cắt histogram tại ngưỡng clip_limit và phân phối lại pixel dư.

    hist: histogram có L bin.
    clip_limit: ngưỡng cắt tối đa ban đầu của mỗi bin.

    Trả về histogram có tổng số pixel được bảo toàn.
    """
    hist = np.asarray(hist, dtype=np.int64)

    if hist.ndim != 1:
        raise ValueError("hist phải là mảng một chiều.")

    if np.any(hist < 0):
        raise ValueError("Histogram không được chứa giá trị âm.")

    if clip_limit is None or clip_limit <= 0:
        return hist.copy()

    limit = max(1, int(clip_limit))
    clipped = np.minimum(hist, limit)
    excess = int(np.sum(hist - clipped))

    # Phân phối đều phần dư cho tất cả các bin.
    num_bins = len(clipped)
    if num_bins == 0:
        return clipped

    bonus, remainder = divmod(excess, num_bins)
    clipped += bonus

    # Phân phối phần dư còn lại theo thứ tự các bin.
    if remainder > 0:
        clipped[:remainder] += 1

    return clipped


def build_tile_luts(img, grid=(8, 8), clip_limit=2.0):
    """
    Xây dựng LUT cho từng ô theo công thức trong tài liệu.

    img: ảnh xám uint8, kích thước (H, W).
    grid: (Gy, Gx), số ô theo chiều dọc và ngang.
    clip_limit: giới hạn ngưỡng cắt so với chiều cao trung bình của histogram.

    Trả về LUT có kích thước (Gy, Gx, 256).
    """
    img = np.asarray(img)

    if img.ndim != 2:
        raise ValueError("Ảnh đầu vào phải là ảnh xám 2 chiều.")

    if img.dtype != np.uint8:
        raise ValueError("Ảnh đầu vào phải có kiểu uint8.")

    H, W = img.shape
    Gy, Gx = grid
    L = 256

    if not (1 <= Gy <= H and 1 <= Gx <= W):
        raise ValueError("Số ô phải nằm trong giới hạn kích thước ảnh.")

    if clip_limit < 1.0:
        raise ValueError("clip_limit phải lớn hơn hoặc bằng 1.0")

    tile_h = H / Gy
    tile_w = W / Gx

    luts = np.zeros((Gy, Gx, L), dtype=np.uint8)

    for y in range(Gy):
        y0 = int(round(y * tile_h))
        y1 = int(round((y + 1) * tile_h))

        for x in range(Gx):
            x0 = int(round(x * tile_w))
            x1 = int(round((x + 1) * tile_w))

            tile = img[y0:y1, x0:x1]
            n_tile = tile.size

            if n_tile == 0:
                luts[y, x] = np.arange(L, dtype=np.uint8)
                continue

            # Histogram của ô.
            hist = np.bincount(
                tile.ravel(), minlength=L
            ).astype(np.int64)

            # Chiều cao trung bình của một bin.
            avg_height = n_tile / L

            # Tính beta trực tiếp từ clip_limit
            beta = avg_height * clip_limit

            # Ngưỡng cắt nguyên.
            clip_limit_int = max(1, int(np.floor(beta)))

            # Cắt histogram và phân phối lại phần dư.
            clipped_hist = clip_histogram(hist, clip_limit_int)

            # CDF và LUT.
            cdf = np.cumsum(clipped_hist, dtype=np.int64)

            lut = np.round(
                (cdf / n_tile) * (L - 1)
            )

            luts[y, x] = np.clip(
                lut, 0, L - 1
            ).astype(np.uint8)

    return luts


def clahe(img, grid=(8, 8), clip_limit=2.0):
    """
    CLAHE với nội suy song tuyến giữa bốn LUT lân cận.

    img: ảnh xám uint8 có kích thước (H, W).
    grid: (Gy, Gx).
    clip_limit: giới hạn ngưỡng cắt.

    Trả về ảnh uint8 có cùng kích thước.
    """
    img = np.asarray(img)

    if img.ndim != 2 or img.dtype != np.uint8:
        raise ValueError("img phải là ảnh xám 2D kiểu uint8.")

    H, W = img.shape
    Gy, Gx = grid

    # 1. Tạo LUT cho từng ô.
    luts = build_tile_luts(
        img, grid=grid, clip_limit=clip_limit
    )

    tile_h = H / Gy
    tile_w = W / Gx

    # 2. Tọa độ tâm pixel theo hệ tọa độ tâm các ô.
    yy, xx = np.indices((H, W), dtype=np.float64)

    fy = (yy + 0.5) / tile_h - 0.5
    fx = (xx + 0.5) / tile_w - 0.5

    # Chỉ số hai hàng và hai cột lân cận.
    y0 = np.floor(fy).astype(np.int32)
    x0 = np.floor(fx).astype(np.int32)

    # Trọng số nội suy.
    b = fy - y0
    a = fx - x0

    y1 = y0 + 1
    x1 = x0 + 1

    # 3. Xử lý biên: giữ trọng số hợp lệ [0, 1].
    a = np.clip(a, 0.0, 1.0)
    b = np.clip(b, 0.0, 1.0)

    y0 = np.clip(y0, 0, Gy - 1)
    y1 = np.clip(y1, 0, Gy - 1)
    x0 = np.clip(x0, 0, Gx - 1)
    x1 = np.clip(x1, 0, Gx - 1)

    # 4. Tra cứu giá trị từ bốn LUT lân cận.
    v = img

    T00 = luts[y0, x0, v].astype(np.float64)
    T01 = luts[y0, x1, v].astype(np.float64)
    T10 = luts[y1, x0, v].astype(np.float64)
    T11 = luts[y1, x1, v].astype(np.float64)

    # 5. Nội suy song tuyến theo công thức (4).
    top = (1.0 - a) * T00 + a * T01
    bottom = (1.0 - a) * T10 + a * T11

    result = (1.0 - b) * top + b * bottom

    return np.clip(
        np.round(result), 0, 255
    ).astype(np.uint8)
