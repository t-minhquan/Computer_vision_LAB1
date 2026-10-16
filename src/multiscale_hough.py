import numpy as np

try:
    from .utils import convolve2d, get_gaussian_kernel
except ImportError:
    from utils import convolve2d, get_gaussian_kernel


def wrap_theta_rho(theta, rho):
    """
    Xử lý đúng bẫy quấn vòng ở theta = 0 và theta = pi (Mục 4.3 trong đề tài):
    Khi mở cửa sổ lân cận quanh theta* ~ 0, phần âm phải quấn về phía pi
    và kèm theo đổi dấu rho.
    Từ phương trình (11), đường thẳng (rho, theta) và (-rho, theta + pi) là cùng một đường.
    Quy chuẩn theta về nửa khoảng [0, pi).
    """
    while theta < 0.0:
        theta += np.pi
        rho = -rho
    while theta >= np.pi:
        theta -= np.pi
        rho = -rho
    return theta, rho


def are_lines_duplicate(rho1, theta1, rho2, theta2, d_theta_thresh=np.radians(8.0), d_rho_thresh=12.0):
    """
    Kiểm tra hai tham số (rho, theta) có cùng biểu diễn một đường thẳng vật lý hay không,
    kể cả trường hợp quấn vòng quanh biên theta = 0 và theta = pi (đổi dấu rho).
    """
    diff_t = abs(theta1 - theta2)
    if diff_t > np.pi / 2.0:
        diff_t = np.pi - diff_t
        diff_r = abs(rho1 + rho2)  # Đổi dấu rho khi theta quấn qua pi
    else:
        diff_r = abs(rho1 - rho2)
    return diff_t <= d_theta_thresh and diff_r <= d_rho_thresh


def hough_accumulate(edges, theta_range, rho_range, n_theta, n_rho,
                     grad_dir=None, delta_deg=None):
    """
    Bỏ phiếu vào mảng tích lũy. Nếu grad_dir khác None, chỉ bỏ phiếu
    trong dải +/- delta_deg quanh hướng gradient (Mục 4.4 trong đề tài).
    
    edges: ảnh nhị phân biên (H, W), giá trị > 0 là điểm biên.
    theta_range: tuple (theta_min, theta_max) tính bằng radian.
    rho_range: tuple (rho_min, rho_max) tính bằng pixel.
    n_theta: số lượng bin góc theta.
    n_rho: số lượng bin khoảng cách rho.
    grad_dir: mảng (H, W) góc gradient (radian) trong khoảng [0, pi) nếu có.
    delta_deg: góc dung sai (độ) quanh hướng gradient.
    
    Trả về: (A, thetas, rhos)
    A: mảng tích lũy (n_rho, n_theta) kiểu int32
    thetas: mảng 1D các giá trị theta tương ứng
    rhos: mảng 1D các giá trị rho tương ứng
    """
    edges = np.asarray(edges)
    thetas = np.linspace(theta_range[0], theta_range[1], n_theta, endpoint=False)
    rhos = np.linspace(rho_range[0], rho_range[1], n_rho)
    
    d_theta = thetas[1] - thetas[0] if n_theta > 1 else 1.0
    d_rho = rhos[1] - rhos[0] if n_rho > 1 else 1.0
    
    # Lấy tọa độ các điểm biên: quy ước ảnh numpy I[y, x] -> y là hàng, x là cột
    y_idxs, x_idxs = np.nonzero(edges)
    num_pts = len(y_idxs)
    
    A = np.zeros((n_rho, n_theta), dtype=np.int32)
    if num_pts == 0:
        return A, thetas, rhos
        
    cos_t = np.cos(thetas)
    sin_t = np.sin(thetas)
    
    if grad_dir is None or delta_deg is None:
        # Bỏ phiếu chuẩn tắc cho mọi góc theta
        # Vector hóa: tính rho cho toàn bộ điểm biên tại từng cột theta để tối ưu tốc độ bằng numpy
        for j in range(n_theta):
            rho_vals = x_idxs * cos_t[j] + y_idxs * sin_t[j]
            r_idx = np.round((rho_vals - rho_range[0]) / d_rho).astype(np.int32)
            valid = (r_idx >= 0) & (r_idx < n_rho)
            if np.any(valid):
                A[:, j] += np.bincount(r_idx[valid], minlength=n_rho)
    else:
        # Bỏ phiếu giới hạn theo hướng gradient (Mục 4.4): theta in [theta_g - delta, theta_g + delta]
        delta_rad = np.radians(delta_deg)
        pts_grad = grad_dir[y_idxs, x_idxs]  # Hướng gradient theta_g của từng điểm biên
        
        for j in range(n_theta):
            th = thetas[j]
            # Khoảng cách góc ngắn nhất có xét tính tuần hoàn mod pi
            diff = np.abs((th - pts_grad + np.pi / 2.0) % np.pi - np.pi / 2.0)
            mask = diff <= delta_rad
            if np.any(mask):
                rho_vals = x_idxs[mask] * cos_t[j] + y_idxs[mask] * sin_t[j]
                r_idx = np.round((rho_vals - rho_range[0]) / d_rho).astype(np.int32)
                valid = (r_idx >= 0) & (r_idx < n_rho)
                if np.any(valid):
                    A[:, j] += np.bincount(r_idx[valid], minlength=n_rho)
                    
    return A, thetas, rhos


def find_peaks(A, n_peaks, nms_radius=3, smooth_sigma=1.0, thetas=None, rhos=None):
    """
    Làm mượt A bằng hàm tích chập của chính nhóm, triệt phi cực đại,
    trả về danh sách (rho, theta, votes) sắp giảm dần.
    
    Nếu thetas và rhos được truyền vào, trả về giá trị thực (rho, theta, votes).
    Nếu không, trả về danh sách chỉ số ô (rho_idx, theta_idx, votes).
    """
    # 1. Làm mượt mảng tích lũy bằng nhân Gauss với tích chập tự viết (Mục 4.5)
    if smooth_sigma > 0:
        kernel_size = int(round(smooth_sigma * 4)) | 1  # Đảm bảo kích thước lẻ
        kernel = get_gaussian_kernel(size=kernel_size, sigma=smooth_sigma)
        A_smooth = convolve2d(A, kernel)
    else:
        A_smooth = A.copy().astype(np.float64)
        
    n_rho, n_theta = A_smooth.shape
    r = nms_radius
    candidates = []
    
    # 2. Triệt phi cực đại (NMS) cục bộ
    for ri in range(n_rho):
        r_start = max(0, ri - r)
        r_end = min(n_rho, ri + r + 1)
        for ti in range(n_theta):
            val = A_smooth[ri, ti]
            if val <= 0:
                continue
            t_start = max(0, ti - r)
            t_end = min(n_theta, ti + r + 1)
            
            patch = A_smooth[r_start:r_end, t_start:t_end]
            if val == np.max(patch):
                candidates.append((ri, ti, int(A[ri, ti]), val))
                
    # Sắp xếp theo số phiếu giảm dần (ưu tiên giá trị làm mượt)
    candidates.sort(key=lambda item: item[3], reverse=True)
    selected = candidates[:n_peaks]
    
    # 3. Trả về kết quả
    if thetas is not None and rhos is not None:
        return [(float(rhos[ri]), float(thetas[ti]), votes) for ri, ti, votes, _ in selected]
    return [(ri, ti, votes) for ri, ti, votes, _ in selected]


def hough_multiscale(edges, grad_dir=None, delta_deg=10.0, n_levels=2,
                     refine_factor=8, n_peaks=5):
    """
    Hough thô-đến-mịn (Coarse-to-fine) theo Mục 4.3 trong đề tài:
    1. Dựng mảng tích lũy thô (Delta_theta0 = 1 độ, Delta_rho0 = 2 px).
    2. Tìm K đỉnh ứng viên trong mảng thô (lọc trùng lặp qua biên 0 và pi).
    3. Với mỗi ứng viên (rho*, theta*), dựng lại mảng tích lũy nhỏ và mịn
       chỉ phủ lân cận [rho* +/- Delta_rho0, theta* +/- Delta_theta0],
       với bước chia nhỏ đi r lần (ví dụ r = 8).
       Chỉ những điểm biên đã bỏ phiếu cho ô thô mới tham gia bỏ phiếu lại.
    4. Lặp thêm 1-2 tầng nếu cần. Xử lý đúng bẫy quấn vòng ở theta = 0 và theta = pi.
    
    Trả về danh sách (rho, theta, votes) đã tinh chỉnh.
    """
    edges = np.asarray(edges)
    h, w = edges.shape
    d_max = np.sqrt(h**2 + w**2)
    
    # Bước 1: Dựng mảng tích lũy thô
    d_theta0 = np.radians(1.0)  # 1 độ
    d_rho0 = 2.0               # 2 pixel
    n_theta0 = int(np.pi / d_theta0)
    n_rho0 = int((2.0 * d_max) / d_rho0) + 1
    
    A_coarse, thetas_c, rhos_c = hough_accumulate(
        edges, (0.0, np.pi), (-d_max, d_max), n_theta0, n_rho0,
        grad_dir=grad_dir, delta_deg=delta_deg
    )
    
    # Bước 2: Tìm các đỉnh trong mảng thô
    # Tìm nhiều ứng viên hơn để lọc bỏ các đỉnh ảo do quấn vòng quanh biên 0 và pi
    raw_peaks = find_peaks(A_coarse, n_peaks=n_peaks * 3, nms_radius=3, smooth_sigma=1.0)
    
    # Lọc bỏ các đỉnh trùng lặp hình học (kể cả quấn vòng mod pi đổi dấu rho)
    unique_coarse_peaks = []
    for r_idx, t_idx, votes in raw_peaks:
        rh = rhos_c[r_idx]
        th = thetas_c[t_idx]
        if not any(are_lines_duplicate(rh, th, rhos_c[ur], thetas_c[ut]) for ur, ut, _ in unique_coarse_peaks):
            unique_coarse_peaks.append((r_idx, t_idx, votes))
        if len(unique_coarse_peaks) >= n_peaks:
            break
            
    y_all, x_all = np.nonzero(edges)
    if len(y_all) == 0:
        return []
        
    refined_lines = []
    
    # Bước 3: Tinh chỉnh từng đỉnh ứng viên
    for r_idx, t_idx, c_votes in unique_coarse_peaks:
        curr_theta = thetas_c[t_idx]
        curr_rho = rhos_c[r_idx]
        
        step_theta = d_theta0
        step_rho = d_rho0
        best_votes = c_votes
        
        # Lọc: "Chỉ những điểm biên đã bỏ phiếu cho ô thô mới tham gia bỏ phiếu lại"
        rhos_cand = x_all * np.cos(curr_theta) + y_all * np.sin(curr_theta)
        cand_mask = np.abs(rhos_cand - curr_rho) <= (step_rho * 1.5)
        if grad_dir is not None and delta_deg is not None:
            pts_grad = grad_dir[y_all, x_all]
            diff = np.abs((curr_theta - pts_grad + np.pi / 2.0) % np.pi - np.pi / 2.0)
            cand_mask &= (diff <= np.radians(delta_deg))
            
        cand_x = x_all[cand_mask]
        cand_y = y_all[cand_mask]
        
        if len(cand_x) == 0:
            final_th, final_rh = wrap_theta_rho(curr_theta, curr_rho)
            refined_lines.append((final_rh, final_th, c_votes))
            continue
            
        # Lặp các tầng tinh chỉnh thô-đến-mịn
        for level in range(1, n_levels):
            n_sub_theta = refine_factor * 2 + 1
            n_sub_rho = refine_factor * 2 + 1
            
            min_th = curr_theta - step_theta
            max_th = curr_theta + step_theta
            min_rh = curr_rho - step_rho
            max_rh = curr_rho + step_rho
            
            sub_thetas = np.linspace(min_th, max_th, n_sub_theta)
            sub_rhos = np.linspace(min_rh, max_rh, n_sub_rho)
            sub_d_th = sub_thetas[1] - sub_thetas[0]
            sub_d_rh = sub_rhos[1] - sub_rhos[0]
            
            sub_A = np.zeros((n_sub_rho, n_sub_theta), dtype=np.int32)
            
            # Bỏ phiếu trong cửa sổ mịn cục bộ
            for ti, th_val in enumerate(sub_thetas):
                rh_vals = cand_x * np.cos(th_val) + cand_y * np.sin(th_val)
                r_bins = np.round((rh_vals - min_rh) / sub_d_rh).astype(np.int32)
                valid = (r_bins >= 0) & (r_bins < n_sub_rho)
                if np.any(valid):
                    sub_A[:, ti] = np.bincount(r_bins[valid], minlength=n_sub_rho)
                    
            # Tìm vị trí đỉnh trong mảng mịn
            best_r_idx, best_t_idx = np.unravel_index(np.argmax(sub_A), sub_A.shape)
            curr_rho = sub_rhos[best_r_idx]
            curr_theta = sub_thetas[best_t_idx]
            best_votes = int(sub_A[best_r_idx, best_t_idx])
            
            # Thu hẹp bước cho tầng tiếp theo
            step_theta /= refine_factor
            step_rho /= refine_factor
            
        # BẪY QUẤN VÒNG: Chuẩn hóa theta về [0, pi) và đổi dấu rho nếu theta vượt qua 0 hoặc pi
        final_theta, final_rho = wrap_theta_rho(curr_theta, curr_rho)
        refined_lines.append((final_rho, final_theta, best_votes))
        
    return refined_lines
