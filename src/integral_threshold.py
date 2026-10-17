"""KỸ THUẬT 2 – NGƯỠNG THÍCH NGHI BẰNG ẢNH TÍCH PHÂN
Theo Computer_Vision 40.pdf, trang 6–8.
Chạy: python ky_thuat_2.py; hình ảnh và CSV sẽ lưu vào ket_qua/.
Bản này có sử dụng AI hỗ trợ chỉnh sửa và kiểm tra mã.
"""

# %% [1] Thu vien va cau hinh
import csv
import time
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')  # chay tren VS Code/terminal khong can cua so giao dien
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

RESULTS = Path(__file__).resolve().parent / 'ket_qua'
RESULTS.mkdir(exist_ok=True)


# %% [2] Bốn hàm yêu cầu ở mục 3.5 của đề

def integral_image(img):
    """Tạo bảng tổng tích lũy S, có thêm hàng 0 và cột 0."""
    img = np.asarray(img)
    if img.ndim != 2:
        raise ValueError("Đầu vào phải là ảnh xám 2 chiều")

    h, w = img.shape
    # Phải chuyển sang int64 TRƯỚC khi cộng dồn để tránh tràn số.
    img64 = img.astype(np.int64)
    S = np.zeros((h + 1, w + 1), dtype=np.int64)
    S[1:, 1:] = np.cumsum(np.cumsum(img64, axis=0), axis=1)
    return S


def box_sum(S, y1, x1, y2, x2):
    """Tổng vùng từ (y1,x1) đến (y2,x2), tính cả các ô biên."""
    # Có hàng/cột 0 nên không cần xử lý riêng khi x1 hoặc y1 bằng 0.
    # Chỉ dùng bốn giá trị trên bảng S, không lặp qua từng pixel.
    y1, x1 = np.asarray(y1), np.asarray(x1)
    y2, x2 = np.asarray(y2), np.asarray(x2)
    return (S[y2 + 1, x2 + 1] - S[y1, x2 + 1]
            - S[y2 + 1, x1] + S[y1, x1])


def local_mean_std(img, radius):
    """Tính trung bình và độ lệch chuẩn ở mỗi pixel bằng hai bảng tích phân."""
    img = np.asarray(img)
    if img.ndim != 2 or img.dtype != np.uint8:
        raise ValueError("Cần ảnh xám uint8 (H, W)")
    if not isinstance(radius, (int, np.integer)) or radius < 0:
        raise ValueError("radius phải là số nguyên không âm")

    h, w = img.shape
    y, x = np.ogrid[:h, :w]  # y là hàng; x là cột
    y1 = np.maximum(y - radius, 0)
    y2 = np.minimum(y + radius, h - 1)
    x1 = np.maximum(x - radius, 0)
    x2 = np.minimum(x + radius, w - 1)

    # Ở mép ảnh, cửa sổ bị cắt nên diện tích thực tế có thể nhỏ hơn.
    area = (y2 - y1 + 1) * (x2 - x1 + 1)

    img64 = img.astype(np.int64)
    S1 = integral_image(img64)
    S2 = integral_image(img64 * img64)  # Không bình phương trực tiếp uint8!
    mean = box_sum(S1, y1, x1, y2, x2) / area
    mean_square = box_sum(S2, y1, x1, y2, x2) / area

    variance = np.maximum(mean_square - mean ** 2, 0.0)
    std = np.sqrt(variance)
    return mean.astype(np.float64), std.astype(np.float64)


def adaptive_threshold(img, radius=15, method='bradley', t=0.15, k=0.34):
    """Nhị phân hóa: chữ tối = 0 (đen), nền = 255 (trắng)."""
    img = np.asarray(img)
    if img.ndim != 2 or img.dtype != np.uint8:
        raise ValueError("Cần ảnh xám uint8 (H, W)")

    mean, std = local_mean_std(img, radius)
    if method in ('bradley', 'bradley-roth'):
        threshold = mean * (1 - t)
    elif method == 'sauvola':
        threshold = mean * (1 + k * (std / 128 - 1))
    else:
        raise ValueError("method chỉ được là 'bradley' hoặc 'sauvola'")

    return np.where(img < threshold, 0, 255).astype(np.uint8)


# %% [3] Kiem thu thuat toan

def run_tests():
    a = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=np.uint8)
    s = integral_image(a)
    assert s.shape == (4, 4) and s.dtype == np.int64
    assert np.all(s[0, :] == 0) and np.all(s[:, 0] == 0)
    assert box_sum(s, 0, 0, 2, 2) == 45
    assert box_sum(s, 1, 1, 2, 2) == 28
    assert np.array_equal(box_sum(s, np.array([0, 1]), 0, 2, 2), [45, 39])
    m, d = local_mean_std(a, radius=1)
    assert np.isclose(m[1, 1], 5)
    assert np.isclose(d[1, 1], np.std(a.astype(float)))
    assert np.isclose(m[0, 0], 3)  # (1+2+4+5)/4
    assert np.isclose(d[0, 0], np.std([1, 2, 4, 5]))
    m0, s0 = local_mean_std(a, radius=0)
    assert np.allclose(m0, a) and np.allclose(s0, 0)
    for meth in ('bradley', 'sauvola'):
        out = adaptive_threshold(a, method=meth)
        assert out.shape == a.shape and out.dtype == np.uint8
        assert set(np.unique(out)).issubset({0, 255})
    big = np.full((200, 300), 255, dtype=np.uint8)
    sbig = integral_image(big.astype(np.int64)**2)
    assert sbig[-1, -1] == 255**2 * 200 * 300  # > 2^31: khong tran int32
    uniform = np.full((40, 40), 120, dtype=np.uint8)
    um, us = local_mean_std(uniform, radius=7)
    assert np.all(um == 120) and np.all(us == 0)
    print('PASS: 4 ham, bien anh, vector hoa, binh phuong int64, variance>=0')


# %% [4] Anh thu tong hop co ground truth, dung de thay ro hieu ung

def text_mask(h=240, w=460, flat=False):
    fig = Figure(figsize=(w / 100, h / 100), dpi=100, facecolor='white')
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(h, 0)
    ax.axis('off')
    if flat:
        ax.text(17, 56, 'BAI TAP CV', fontsize=26, fontweight='black', color='black')
        ax.text(17, 100, 'NEN PHANG', fontsize=18, fontweight='bold', color='black')
        ax.text(17, 147, 'SAUVOLA', fontsize=24, fontweight='black', color='black')
        # Nua ben phai va phan duoi co vung phang KHONG co chu
    else:
        ax.text(20, 62, 'COMPUTER VISION', fontsize=24, fontweight='black', color='black')
        ax.text(20, 118, 'BRADLEY ROTH', fontsize=22, fontweight='bold', color='black')
        ax.text(20, 170, 'Sauvola & Integral Image', fontsize=18, fontweight='bold', color='black')
        ax.text(20, 215, '2026', fontsize=19, fontweight='bold', color='black')
    canvas.draw()
    rgba = np.asarray(canvas.buffer_rgba())
    mask = np.zeros((h, w), dtype=bool)
    ch, cw = rgba.shape[:2]
    mask[:min(h,ch), :min(w,cw)] = rgba[:min(h,ch), :min(w,cw), 0] < 190
    return mask


def make_scene(h=240, w=460, flat=False, seed=42):
    yy, xx = np.mgrid[:h, :w]
    ink = text_mask(h, w, flat=flat)
    rng = np.random.default_rng(seed)
    if flat:
        # Vung nen phang + nhieu gauss du de Bradley nhan nham thanh cham den.
        background = 125.0 + 1.5 * np.sin(xx / 70.0)
        sigma_noise = 18.0
        darkness = 88.0
    else:
        # Chieu sang KHONG deu trai->phai + bong chay doc.
        background = 80.0 + 158.0 * xx / max(w-1, 1) + 14.0 * np.sin(yy / 45.0)
        sigma_noise = 2.0
        darkness = 88.0
    img = np.clip(background - darkness * ink + rng.normal(0, sigma_noise, (h, w)),
                  0, 255).astype(np.uint8)
    return img, ink


def save_image(img, filename, title=None):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.imshow(img, cmap='gray', vmin=0, vmax=255, interpolation='nearest')
    if title:
        ax.set_title(title)
    ax.axis('off')
    fig.tight_layout()
    fig.savefig(RESULTS / filename, dpi=150)
    plt.close(fig)


def grid_plot(imgs, titles, filename, cols, width=19, row_h=2.75):
    rows = int(np.ceil(len(imgs) / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(width, row_h*rows), squeeze=False)
    for i, ax in enumerate(axes.flat):
        if i < len(imgs):
            ax.imshow(imgs[i], cmap='gray', vmin=0, vmax=255, interpolation='nearest')
            ax.set_title(titles[i], fontsize=10)
        ax.axis('off')
    fig.tight_layout(pad=1.0)
    fig.savefig(RESULTS / filename, dpi=155)
    plt.close(fig)


def segmentation_scores(binary, ink, region=None):
    pred = binary == 0
    valid = np.ones(ink.shape, bool) if region is None else region
    tp = np.count_nonzero(pred & ink & valid)
    fp = np.count_nonzero(pred & ~ink & valid)
    fn = np.count_nonzero(~pred & ink & valid)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2*precision*recall/(precision+recall) if precision+recall else 0.0
    return (precision, recall, f1, fp)


# %% [5] Thi nghiem A: quet >=5 radius va >=3 gia tri t/k

def experiment_a(img):
    radii = [1, 3, 7, 15, 31, 127, 511]
    t_values = [0.05, 0.15, 0.25]
    k_values = [0.20, 0.34, 0.50]
    b_imgs = [adaptive_threshold(img, radius=r, t=t) for t in t_values for r in radii]
    b_titles = [f'r={r}, t={t:.2f}' for t in t_values for r in radii]
    grid_plot(b_imgs, b_titles, 'A_Bradley_quet_radius_t.png', cols=len(radii), width=21, row_h=3.0)
    s_imgs = [adaptive_threshold(img, radius=r, method='sauvola', k=k)
              for k in k_values for r in radii]
    s_titles = [f'r={r}, k={k:.2f}' for k in k_values for r in radii]
    grid_plot(s_imgs, s_titles, 'A_Sauvola_quet_radius_k.png', cols=len(radii), width=21, row_h=3.0)

    # Chu co net day: voi r=1, pixel ben trong net khong du khac biet voi lan can.
    compare = [img] + [adaptive_threshold(img, radius=r, t=0.15) for r in [1, 3, 15, 511]]
    grid_plot(compare, ['Anh goc', 'r=1: rong ruot', 'r=3', 'r=15: phu hop',
                       'r=511: nguong toan cuc'], 'A_hieu_ung_ban_kinh.png', cols=5, width=19)

    # r >= max(H, W) thi moi pixel deu su dung cung cua so la toan bo anh.
    global_mean = float(img.mean())
    global_binary = np.where(img < global_mean*(1-0.15), 0, 255).astype(np.uint8)
    assert np.array_equal(adaptive_threshold(img, radius=511, t=0.15), global_binary)
    print('A: 7 radius x 3 t; 7 radius x 3 k; r=511 trung dung nguong mean toan cuc.')
    return radii, t_values, k_values


# %% [6] Thi nghiem B: fixed, Otsu, Bradley-Roth, Sauvola

def otsu_manual(img):
    """Otsu tu np.bincount va between-class variance; KHONG dung ham cam."""
    hist = np.bincount(img.ravel(), minlength=256).astype(np.float64)
    prob = hist / hist.sum()
    w0 = np.cumsum(prob)
    mu0 = np.cumsum(prob * np.arange(256))
    total_mean = mu0[-1]
    score = np.zeros(256, dtype=np.float64)
    valid = (w0 > 0) & (w0 < 1)
    score[valid] = ((total_mean*w0[valid] - mu0[valid])**2 /
                    (w0[valid] * (1-w0[valid])))
    return int(np.argmax(score[:-1]))


def experiment_b(uneven, uneven_gt, flat, flat_gt):
    rows = []
    for label, img, truth in [('anh_sang_khong_deu', uneven, uneven_gt),
                              ('nen_phang_rong', flat, flat_gt)]:
        otsu_t = otsu_manual(img)
        outputs = [('Anh goc', img),
                   ('Nguong co dinh 128', np.where(img < 128, 0, 255).astype(np.uint8)),
                   (f'Otsu toan cuc (T={otsu_t})', np.where(img <= otsu_t, 0, 255).astype(np.uint8)),
                   ('Bradley-Roth r=15 t=.15', adaptive_threshold(img, 15, 'bradley')),
                   ('Sauvola r=15 k=.34', adaptive_threshold(img, 15, 'sauvola'))]
        grid_plot([x[1] for x in outputs], [x[0] for x in outputs],
                  'B_so_sanh_'+label+'.png', cols=5, width=20, row_h=3.25)
        for method, result in outputs[1:]:
            p, r, f1, fp = segmentation_scores(result, truth)
            rows.append((label, method, round(p, 5), round(r, 5), round(f1, 5), fp))

        if label == 'nen_phang_rong':
            # Vung nen phang khong co chu de do cham den gia (false positives).
            right = np.zeros(img.shape, bool)
            right[:, img.shape[1]*2//3:] = True
            print('B: ti le pixel nen phang bi nhan nham la chu:')
            for method, result in outputs[1:]:
                fp = np.count_nonzero((result == 0) & right & ~truth)
                count = np.count_nonzero(right & ~truth)
                rate = 100*fp/count
                print(f'   {method:32s}: {rate:6.2f}%')
    with open(RESULTS/'B_chi_so_so_sanh.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['anh', 'phuong_phap', 'precision', 'recall', 'f1', 'false_positive_pixels'])
        writer.writerows(rows)
    return rows


# %% [7] Thi nghiem C: 3 cach tinh mean, cung xu ly bien

def local_mean_direct(img, radius):
    """Tich chap hop truc tiep: O(r^2) / pixel, vong lap tren kernel (khong loop pixel)."""
    h, w = img.shape
    pad = np.pad(img.astype(np.float64), radius, mode='constant')
    sums = np.zeros((h, w), dtype=np.float64)
    for dy in range(2*radius+1):
        for dx in range(2*radius+1):
            sums += pad[dy:dy+h, dx:dx+w]
    yy, xx = np.ogrid[:h, :w]
    area = ((np.minimum(yy+radius,h-1) - np.maximum(yy-radius,0) + 1)
            * (np.minimum(xx+radius,w-1) - np.maximum(xx-radius,0) + 1))
    return sums/area


def local_mean_separable(img, radius):
    """Tich chap hop 2 lan 1D: O(r) / pixel, khong dung boxFilter/blur."""
    h, w = img.shape
    padded = np.pad(img.astype(np.float64), ((0,0),(radius,radius)))
    horiz = np.zeros((h,w), dtype=np.float64)
    for dx in range(2*radius+1):
        horiz += padded[:,dx:dx+w]
    padded = np.pad(horiz, ((radius,radius),(0,0)))
    sums = np.zeros((h,w), dtype=np.float64)
    for dy in range(2*radius+1):
        sums += padded[dy:dy+h,:]
    yy,xx=np.ogrid[:h,:w]
    area = ((np.minimum(yy+radius,h-1)-np.maximum(yy-radius,0)+1)
            * (np.minimum(xx+radius,w-1)-np.maximum(xx-radius,0)+1))
    return sums/area


def local_mean_integral(img, radius):
    """Dung chi 1 summed-area table cho mean: O(HW) tinh S, O(1) / pixel."""
    h, w = img.shape
    s = integral_image(img)
    yy, xx = np.ogrid[:h, :w]
    y1, y2 = np.maximum(yy-radius,0), np.minimum(yy+radius,h-1)
    x1, x2 = np.maximum(xx-radius,0), np.minimum(xx+radius,w-1)
    area = (y2-y1+1)*(x2-x1+1)
    return box_sum(s,y1,x1,y2,x2)/area


def experiment_c():
    test_img, _ = make_scene(h=64,w=64, seed=88)
    radii = [1,2,4,8,16,32,64]
    funcs = [local_mean_direct, local_mean_separable, local_mean_integral]
    labels = ['Truc tiep O(r^2)', 'Tach duoc O(r)', 'Anh tich phan O(1)']
    samples = 5
    results = np.zeros((3,len(radii)),dtype=np.float64)
    for j, r in enumerate(radii):
        reference = local_mean_integral(test_img,r)
        for i, fn in enumerate(funcs):
            durations = []
            for _ in range(samples):
                start = time.perf_counter()
                got = fn(test_img,r)
                durations.append((time.perf_counter()-start)*1000)
                assert np.allclose(reference,got,rtol=1e-12,atol=1e-10), (labels[i],r)
            results[i,j] = np.median(durations)

    fig, ax = plt.subplots(figsize=(10,5.5))
    for values, label in zip(results,labels):
        ax.plot(radii,values,marker='o',linewidth=2,label=label)
    ax.set_yscale('log')
    ax.set_xticks(radii)
    ax.set_xlabel('Ban kinh cua so r (pixel)')
    ax.set_ylabel('Thoi gian (ms) - thang log')
    ax.set_title('Thi nghiem C: truc tiep vs tach duoc vs anh tich phan')
    ax.grid(True, which='both', alpha=.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS/'C_3_duong_thoi_gian_log.png',dpi=180)
    plt.close(fig)
    with open(RESULTS/'C_bang_thoi_gian.csv','w',newline='',encoding='utf-8') as file:
        writer=csv.writer(file)
        writer.writerow(['radius','direct_ms','separable_ms','integral_ms'])
        for j,r in enumerate(radii):
            writer.writerow([r,*[round(float(results[i,j]),6) for i in range(3)]])
    print('C: 7 radius, 3 phuong phap, moi diem median 5 lan; ket qua 3 cach giong nhau.')
    for j,r in enumerate(radii):
        print(f'   r={r:>2} | direct={results[0,j]:9.3f}ms'
              f' | separable={results[1,j]:8.3f}ms | integral={results[2,j]:8.3f}ms')
    return radii,results


# %% [8] Toan bo thuc nghiem

def main():
    run_tests()
    uneven, uneven_gt = make_scene()
    flat, flat_gt = make_scene(flat=True)
    save_image(uneven, 'anh_nguon_chieu_sang_khong_deu.png', 'Anh co chieu sang khong deu')
    save_image(flat, 'anh_nguon_nen_phang_rong.png', 'Anh co nen phang rong + nhieu')
    grid_plot([uneven,flat], ['Anh sang khong deu','Nen phang rong + nhieu'],
              'anh_nguon_so_sanh.png',cols=2,width=12,row_h=3.25)
    experiment_a(uneven)
    experiment_b(uneven,uneven_gt,flat,flat_gt)
    experiment_c()
    print('HOAN TAT: xem hinh anh + CSV trong', RESULTS)


if __name__ == '__main__':
    main()
