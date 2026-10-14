import numpy as np
from .utils import convolve2d, get_gaussian_kernel

def hough_accumulate(edges, theta_range, rho_range, n_theta, n_rho, grad_dir=None, delta_deg=None):
    """
    Bỏ phiếu vào mảng tích lũy Hough.
    edges: ảnh nhị phân biên (H, W), giá trị > 0 là điểm biên.
    theta_range: tuple (theta_min, theta_max) tính bằng radian.
    rho_range: tuple (rho_min, rho_max) tính bằng pixel.
    n_theta: số lượng bin góc theta.
    n_rho: số lượng bin khoảng cách rho.
    grad_dir: mảng (H, W) góc gradient (radian) trong khoảng [0, pi) nếu có.
    delta_deg: góc dung sai (độ) quanh hướng gradient.
    
    Trả về:
    A: mảng tích lũy (n_rho, n_theta) kiểu int32
    thetas: mảng 1D các giá trị theta tương ứng
    rhos: mảng 1D các giá trị rho tương ứng
    """
    edges = np.asarray(edges)
    thetas = np.linspace(theta_range[0], theta_range[1], n_theta, endpoint=False)
    rhos = np.linspace(rho_range[0], rho_range[1], n_rho)
    
    d_theta = thetas[1] - thetas[0] if n_theta > 1 else 1.0
    d_rho = rhos[1] - rhos[0] if n_rho > 1 else 1.0
    
    # Lấy tọa độ các điểm biên (y là hàng, x là cột)
    y_idxs, x_idxs = np.nonzero(edges)
    num_pts = len(y_idxs)
    
    A = np.zeros((n_rho, n_theta), dtype=np.int32)
    if num_pts == 0:
        return A, thetas, rhos
        
    cos_t = np.cos(thetas)
    sin_t = np.sin(thetas)
    
    if grad_dir is None or delta_deg is None:
        # Bỏ phiếu chuẩn tắc cho mọi góc theta
        # Vector hóa: với mỗi điểm (x, y), rho = x * cos(theta) + y * sin(theta)
        for i in range(num_pts):
            x = x_idxs[i]
            y = y_idxs[i]
            rho_vals = x * cos_t + y * sin_t
            
            # Quy đổi rho về chỉ số bin trong mảng A
            rho_bins = np.round((rho_vals - rho_range[0]) / d_rho).astype(np.int32)
            valid = (rho_bins >= 0) & (rho_bins < n_rho)
            
            theta_bins = np.nonzero(valid)[0]
            valid_rho_bins = rho_bins[valid]
            
            for t_idx, r_idx in zip(theta_bins, valid_rho_bins):
                A[r_idx, t_idx] += 1
    else:
        # Bỏ phiếu giới hạn theo hướng gradient (tiết kiệm thời gian, tăng SNR)
        delta_rad = np.radians(delta_deg)
        pts_grad = grad_dir[y_idxs, x_idxs]
        
        for i in range(num_pts):
            x = x_idxs[i]
            y = y_idxs[i]
            g_theta = pts_grad[i]
            
            # Pháp tuyến của đường thẳng theo hướng gradient
            # Tính khoảng cách góc ngắn nhất có xét quấn vòng quanh mod pi
            diff = np.abs((thetas - g_theta + np.pi / 2.0) % np.pi - np.pi / 2.0)
            valid_theta_mask = diff <= delta_rad
            
            if not np.any(valid_theta_mask):
                continue
                
            selected_thetas = thetas[valid_theta_mask]
            selected_cos = np.cos(selected_thetas)
            selected_sin = np.sin(selected_thetas)
            
            rho_vals = x * selected_cos + y * selected_sin
            rho_bins = np.round((rho_vals - rho_range[0]) / d_rho).astype(np.int32)
            
            valid_r = (rho_bins >= 0) & (rho_bins < n_rho)
            theta_indices = np.nonzero(valid_theta_mask)[0][valid_r]
            rho_indices = rho_bins[valid_r]
            
            for t_idx, r_idx in zip(theta_indices, rho_indices):
                A[r_idx, t_idx] += 1
                
    return A, thetas, rhos

def find_peaks(A, n_peaks, nms_radius=3, smooth_sigma=1.0):
    """
    Tìm đỉnh trong mảng tích lũy:
    1. Làm mượt mảng A bằng hàm tích chập (nhân Gauss).
    2. Triệt phi cực đại (NMS) trong lân cận bán kính nms_radius.
    3. Trả về danh sách (rho_idx, theta_idx, votes) sắp giảm dần theo số phiếu.
    """
    # 1. Làm mượt bằng tích chập 2D tự viết
    if smooth_sigma > 0:
        kernel_size = int(round(smooth_sigma * 4)) | 1  # Đảm bảo kích thước lẻ
        kernel = get_gaussian_kernel(size=kernel_size, sigma=smooth_sigma)
        A_smooth = convolve2d(A, kernel)
    else:
        A_smooth = A.copy().astype(np.float64)
        
    n_rho, n_theta = A_smooth.shape
    r = nms_radius
    peaks = []
    
    # 2. Triệt phi cực đại cục bộ
    # Quét qua từng ô và kiểm tra xem có phải cực đại nghiêm ngặt trong cửa sổ (2r+1) x (2r+1) không
    for ri in range(n_rho):
        r_start = max(0, ri - r)
        r_end = min(n_rho, ri + r + 1)
        for ti in range(n_theta):
            val = A_smooth[ri, ti]
            if val <= 0:
                continue
                
            # Xử lý quấn vòng theta theo phương ngang nếu cần, ở đây xét cửa sổ cục bộ
            t_start = max(0, ti - r)
            t_end = min(n_theta, ti + r + 1)
            
            patch = A_smooth[r_start:r_end, t_start:t_end]
            if val == np.max(patch):
                # Lưu giá trị phiếu gốc để trung thực với số điểm bỏ phiếu
                original_votes = A[ri, ti]
                peaks.append((ri, ti, original_votes, val))
                
    # Sắp xếp theo số phiếu giảm dần (ưu tiên giá trị đã làm mượt)
    peaks.sort(key=lambda x: x[3], reverse=True)
    
    # Chỉ lấy tối đa n_peaks đỉnh
    selected = [(p[0], p[1], p[2]) for p in peaks[:n_peaks]]
    return selected

def wrap_theta_rho(theta, rho):
    """
    Xử lý đúng bẫy quấn vòng góc theta quanh 0 và pi:
    Đường thẳng (rho, theta) và (-rho, theta + pi) hoặc (-rho, theta - pi) là một.
    Quy chuẩn theta về [0, pi).
    """
    while theta < 0.0:
        theta += np.pi
        rho = -rho
    while theta >= np.pi:
        theta -= np.pi
        rho = -rho
    return theta, rho

def hough_multiscale(edges, grad_dir=None, delta_deg=10.0, n_levels=2, refine_factor=8, n_peaks=5):
    """
    Hough thô-đến-mịn (Coarse-to-fine).
    Tầng 1: Chạy Hough thô trên toàn ảnh.
    Tầng 2+: Với mỗi đỉnh ứng viên, dựng lại mảng tích lũy nhỏ và mịn quanh lân cận đỉnh,
             xử lý quấn vòng góc theta quanh 0 và pi (đổi dấu rho).
             
    Trả về danh sách các đường thẳng tinh chỉnh: list of (rho, theta, votes).
    """
    h, w = edges.shape
    d_max = np.sqrt(h**2 + w**2)
    
    # Tham số tầng thô (Level 0)
    # Ví dụ d_theta0 = 1 độ (~0.0174 rad), d_rho0 = 2 pixel
    d_theta0 = np.radians(1.0)
    d_rho0 = 2.0
    n_theta0 = int(np.pi / d_theta0)
    n_rho0 = int((2.0 * d_max) / d_rho0)
    
    # 1. Bỏ phiếu thô
    A_coarse, thetas_c, rhos_c = hough_accumulate(
        edges, (0.0, np.pi), (-d_max, d_max), n_theta0, n_rho0,
        grad_dir=grad_dir, delta_deg=delta_deg
    )
    
    # Tìm các đỉnh ở tầng thô
    coarse_peaks = find_peaks(A_coarse, n_peaks=n_peaks, nms_radius=3, smooth_sigma=1.0)
    
    refined_lines = []
    
    # 2. Tinh chỉnh từng đỉnh ứng viên
    for r_idx, t_idx, votes in coarse_peaks:
        curr_theta = thetas_c[t_idx]
        curr_rho = rhos_c[r_idx]
        
        step_theta = d_theta0
        step_rho = d_rho0
        
        # Tinh chỉnh qua các tầng con
        for level in range(1, n_levels):
            # Cửa sổ lân cận: [rho - step_rho, rho + step_rho], [theta - step_theta, theta + step_theta]
            min_th = curr_theta - step_theta
            max_th = curr_theta + step_theta
            min_rh = curr_rho - step_rho
            max_rh = curr_rho + step_rho
            
            # Kích thước mảng mịn cục bộ
            n_sub_theta = refine_factor * 2 + 1
            n_sub_rho = refine_factor * 2 + 1
            
            # Tọa độ các điểm biên trong ảnh
            y_pts, x_pts = np.nonzero(edges)
            
            sub_thetas = np.linspace(min_th, max_th, n_sub_theta)
            sub_rhos = np.linspace(min_rh, max_rh, n_sub_rho)
            
            sub_A = np.zeros((n_sub_rho, n_sub_theta), dtype=np.int32)
            
            sub_d_th = sub_thetas[1] - sub_thetas[0]
            sub_d_rh = sub_rhos[1] - sub_rhos[0]
            
            # Bỏ phiếu trong vùng lân cận mịn
            for x, y in zip(x_pts, y_pts):
                for ti, th_val in enumerate(sub_thetas):
                    # BẪY QUÁN VÒNG: Chuẩn hóa theta và đổi dấu rho nếu theta vượt ra ngoài [0, pi)
                    th_norm, rh_calc = wrap_theta_rho(th_val, x * np.cos(th_val) + y * np.sin(th_val))
                    
                    # Nếu th_norm quay lại khoảng gốc nhưng dấu rho đã được tính chuẩn
                    r_bin = int(round((rh_calc - min_rh) / sub_d_rh))
                    if 0 <= r_bin < n_sub_rho:
                        sub_A[r_bin, ti] += 1
                        
            # Tìm cực đại trong mảng mịn
            max_idx = np.unravel_index(np.argmax(sub_A), sub_A.shape)
            best_r_idx, best_t_idx = max_idx
            curr_theta = sub_thetas[best_t_idx]
            curr_rho = sub_rhos[best_r_idx]
            votes = sub_A[best_r_idx, best_t_idx]
            
            # Thu hẹp bước cho tầng tiếp theo
            step_theta /= refine_factor
            step_rho /= refine_factor
            
        # Chuẩn hóa kết quả cuối cùng về miền chuẩn theta in [0, pi)
        final_theta, final_rho = wrap_theta_rho(curr_theta, curr_rho)
        refined_lines.append((final_rho, final_theta, votes))
        
    return refined_lines
