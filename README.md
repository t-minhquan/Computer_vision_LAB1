# Bài tập lớn hợp nhất: Toán tử điểm, toán tử lân cận và phép biến đổi affine
**Môn học**: Thị giác máy tính (Mã môn: 121036)  
**Trường**: Đại học Giao thông vận tải TP.HCM (UTH)

---

## 1. Giới thiệu dự án

Dự án cài đặt và kiểm nghiệm 3 kỹ thuật nâng cao mở rộng từ các toán tử cơ bản trong thị giác máy tính:
1. **CLAHE (Contrast Limited Adaptive Histogram Equalization)**:
   - Cân bằng lược đồ xám thích nghi với giới hạn tương phản.
   - Chia lưới $Gy \times Gx$, cắt gọt và tái phân phối phần dư $E$ chia đều để bảo toàn tổng số điểm ảnh.
   - Nội suy song tuyến trực tiếp 4 giá trị vô hướng trong bảng tra LUT tại mỗi điểm ảnh (tránh lỗi lãng phí bộ nhớ khi nội suy giữa các ảnh).
2. **Ngưỡng thích nghi bằng ảnh tích phân (Integral Image Adaptive Thresholding)**:
   - Dựng bảng tích phân $S$ với kích thước $(H+1, W+1)$, đệm viền 0 ở hàng và cột đầu tiên, ép kiểu `int64` chống tràn số.
   - Truy vấn tổng chữ nhật $O(1)$ bằng 4 phép truy xuất bộ nhớ.
   - Hỗ trợ cả 2 thuật toán: **Bradley–Roth** (dựa trên trung bình cục bộ) và **Sauvola** (kết hợp trung bình và phương sai cục bộ).
   - Xử lý triệt để bẫy triệt tiêu dấu phẩy động bằng `np.maximum(var, 0.0)` tránh lỗi NaN.
3. **Biến đổi Hough đa tỉ lệ (Multiscale Hough Transform)**:
   - Bỏ phiếu vào mảng tích lũy Hough kết hợp hướng gradient ($\theta_g \pm \delta$) giúp giảm nhiễu và tăng SNR.
   - Làm mượt mảng tích lũy bằng nhân Gauss và triệt phi cực đại (NMS).
   - Chiến lược thô-đến-mịn (Coarse-to-Fine) với việc xử lý chính xác bẫy quấn vòng góc $\theta$ quanh $0$ và $\pi$ kèm đổi dấu $\rho \leftarrow -\rho$, bảo toàn các đường gần thẳng đứng.

---

## 2. Cấu trúc thư mục

```text
Computor_vision_LAB1/
├── Computer_Vision 40.md          # Tài liệu mô tả bài tập lớn gốc
├── README.md                      # Báo cáo và hướng dẫn dự án
├── .agent/                        # Cấu hình AI Assistant & Prompts (Quy chuẩn mục 5.1)
│   ├── prompt_templates.md        # Các mẫu prompt chuẩn để sinh code thí nghiệm
│   └── workflows.md               # Quy trình triển khai và nộp bài
├── src/                           # Thuật toán cốt lõi (Tự viết, không dùng thư viện ngoài)
│   ├── __init__.py
│   ├── clahe.py                   # clip_histogram, build_tile_luts, clahe
│   ├── integral_threshold.py      # integral_image, box_sum, local_mean_std, adaptive_threshold
│   ├── multiscale_hough.py        # hough_accumulate, find_peaks, hough_multiscale
│   └── utils.py                   # convolve2d, get_gaussian_kernel
└── tests/                         # Bộ kiểm thử tự động
    ├── test_clahe.py              # Kiểm thử bảo toàn tổng pixel và dải giá trị
    ├── test_integral.py           # Kiểm thử truy vấn O(1) và tránh lỗi NaN
    └── test_hough.py              # Kiểm thử bẫy quấn vòng góc quanh 0 và 180 độ
```

---

## 3. Hướng dẫn chạy kiểm thử tự động

Dự án đã được tích hợp bộ unit test kiểm tra toàn bộ các bẫy thuật toán được đề bài cảnh báo. Chạy lệnh sau tại thư mục gốc:

```powershell
python -m unittest discover tests
```

Kết quả mong đợi:
```text
Ran 9 tests in 0.463s
OK
```

---

## 4. Hướng dẫn làm phần Thí nghiệm minh họa (Jupyter Notebook)

Theo **Mục 5.1 của đề tài**:
- Phần cài đặt trong `src/` là tự viết hoàn toàn.
- Phần thí nghiệm trong Jupyter Notebook được phép sử dụng AI hỗ trợ (để sinh dữ liệu mẫu, vẽ đồ thị, quét tham số).
- Trước mỗi ô code có sử dụng AI, bạn chỉ cần mở file [`.agent/prompt_templates.md`](file:///.agent/prompt_templates.md), chép nguyên văn mẫu khai báo `### Có dùng AI hỗ trợ` vào Notebook.
