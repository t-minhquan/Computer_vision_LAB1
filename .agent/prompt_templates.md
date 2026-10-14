# Prompt Templates phục vụ sinh viên thực hiện phần Thí nghiệm minh họa (Theo Mục 5.1 - UTH 121036)

> **Lưu ý quan trọng từ Đề tài**:
> - Phần Cài đặt thuật toán lõi (`src/`): Tự viết bằng tay, không dùng AI.
> - Phần Thí nghiệm minh họa (`notebooks/`): Được phép dùng AI để sinh ảnh mẫu, quét tham số, vẽ biểu đồ.
> - Mọi prompt dùng sinh mã cho thí nghiệm **bắt buộc phải chép nguyên văn** vào Notebook ngay trước ô code tương ứng theo format dưới đây.

---

## 1. Mẫu Khai báo bắt buộc trong Notebook (.ipynb)

```markdown
### Có dùng AI hỗ trợ
- **Công cụ**: <Tên AI, ví dụ: ChatGPT 4o / Claude 3.5 Sonnet / Gemini 2.5 Pro>
- **Mục đích**: <Sinh ảnh tổng hợp kiểm thử / Quét lưới tham số / Vẽ đồ thị thời gian log-scale>
- **Prompt**:
> <Chép nguyên văn prompt bạn đã nhập vào ô chat của AI>
- **Đã sửa lại những gì**: <Mô tả các chỉnh sửa nhỏ để khớp với hàm trong file src/ hoặc định dạng dữ liệu>
```

---

## 2. Các Prompt mẫu sẵn dùng cho từng Kỹ thuật

### Prompt cho Kỹ thuật 1: CLAHE (Mục 2.6)

#### Prompt 1.1: Quét tham số lưới (clip_limit và grid)
```text
Hãy viết cho tôi một đoạn mã Python sử dụng Matplotlib và NumPy để thực hiện thí nghiệm quét tham số cho hàm clahe(img, grid, clip_limit):
1. Quét grid qua 4 giá trị: (2, 2), (4, 4), (8, 8), (16, 16).
2. Quét clip_limit qua 4 giá trị: 1.0, 2.0, 5.0, 20.0.
3. Hiển thị kết quả dưới dạng lưới ảnh (subplot grid 4x4) kèm tiêu đề rõ ràng cho từng ô.
4. Đoạn mã nhận đầu vào là một ảnh xám (H, W) uint8 và gọi hàm `from src.clahe import clahe`.
```

#### Prompt 1.2: So sánh 4 phương pháp (Kéo giãn, Gamma, HE toàn cục, CLAHE)
```text
Hãy viết đoạn mã Python so sánh 4 kỹ thuật tăng cường tương phản trên cùng 1 ảnh xám:
1. Kéo giãn tương phản tuyến tính (Linear Contrast Stretching).
2. Hiệu chỉnh Gamma (Gamma Correction với gamma = 0.5 hoặc 1.5).
3. Cân bằng lược đồ xám toàn cục (Global Histogram Equalization - dùng LUT tự tính).
4. CLAHE (dùng hàm clahe từ src.clahe).
Vẽ 2 hàng x 4 cột: hàng trên hiển thị 4 ảnh kết quả, hàng dưới hiển thị histogram tương ứng của từng ảnh.
```

---

### Prompt cho Kỹ thuật 2: Ngưỡng thích nghi & Ảnh tích phân (Mục 3.6)

#### Prompt 2.1: Quét tham số radius và t / k
```text
Hãy viết đoạn mã Python minh họa ảnh hưởng của tham số lên thuật toán ngưỡng thích nghi:
1. Quét bán kính radius qua 5 giá trị: 5, 15, 30, 60, 120.
2. Quét hệ số t (cho Bradley) qua 3 giá trị: 0.05, 0.15, 0.3.
3. Vẽ lưới ảnh kết quả nhị phân (subplot 3x5) để minh họa hiện tượng: radius quá nhỏ làm chữ bị rỗng ruột, radius quá lớn thoái hóa về ngưỡng toàn cục.
Dùng hàm `from src.integral_threshold import adaptive_threshold`.
```

#### Prompt 2.2: So sánh Ngưỡng cố định, Otsu, Bradley-Roth và Sauvola
```text
Hãy viết mã so sánh 4 phương pháp phân ngưỡng trên một ảnh tài liệu có ánh sáng không đều và có một vùng nền phẳng rộng:
1. Ngưỡng cố định toàn cục (Manual Fixed Threshold, T = 127).
2. Ngưỡng Otsu toàn cục.
3. Bradley-Roth (dùng ảnh tích phân, radius=15, t=0.15).
4. Sauvola (dùng 2 ảnh tích phân, radius=15, k=0.34).
Hiển thị 4 kết quả cạnh nhau để chỉ ra rõ: Otsu hỏng ở vùng bóng tối, Bradley bị nhiễu ở vùng nền phẳng, và Sauvola khắc phục triệt để như thế nào.
```

#### Prompt 2.3: Đo thời gian chạy và vẽ đường cong O(1) thang Log-Log
```text
Hãy viết đoạn script đo thời gian chạy của 3 cách tính trung bình cục bộ khi thay đổi bán kính r in [1, 2, 4, 8, 16, 32, 64]:
1. Tích chập trực tiếp nhân hộp (Direct 2D Box Convolution - O(r^2)).
2. Tích chập tách được 2 nhân 1D (Separable Filter - O(r)).
3. Ảnh tích phân (Integral Image / Box Sum - O(1)).
Dùng time hoặc timeit đo trên ảnh 512x512, lặp lại 5 lần lấy trung bình.
Vẽ biểu đồ với trục X là bán kính r (thang log2) và trục Y là thời gian thực thi (thang log), cho thấy 2 đường đầu dốc lên và đường ảnh tích phân hoàn toàn nằm ngang.
```

---

### Prompt cho Kỹ thuật 3: Biến đổi Hough đa tỉ lệ (Mục 4.7)

#### Prompt 3.1: Sinh ảnh kiểm thử tổng hợp (Ground Truth)
```text
Hãy viết một hàm Python sinh ảnh biên nhị phân (edges) kích thước 200x200 chứa các đường thẳng có ground truth (rho0, theta0) biết trước:
1. Một đường thẳng gần thẳng đứng: theta = 0.5 độ hoặc 179.5 độ.
2. Một đoạn thẳng rất dài (150 px) và một đoạn thẳng rất ngắn (20 px) kèm nhiễu vị trí ngẫu nhiên +/- 1 px.
Trả về ảnh edges và danh sách tham số đường thẳng chính xác để làm đáp án chuẩn.
```

#### Prompt 3.2: So sánh Hough thô, Hough mịn và Hough đa tỉ lệ Coarse-to-Fine
```text
Hãy viết đoạn mã so sánh 3 phương pháp phát hiện đường thẳng trên cùng ảnh tổng hợp:
1. Hough chuẩn tắc ở độ phân giải thô (d_theta = 1 độ, d_rho = 2 px).
2. Hough chuẩn tắc ở độ phân giải mịn (d_theta = 0.1 độ, d_rho = 0.5 px).
3. Hough đa tỉ lệ (Coarse-to-Fine với 2 tầng, refine_factor=8).
Hiển thị:
- Mảng tích lũy Hough của từng cách (dạng ảnh heatmap).
- Bảng so sánh sai số góc abs(theta_est - theta_true), tỉ số đỉnh trên nền (SNR), và thời gian chạy.
- Minh họa việc bật/tắt bỏ phiếu theo hướng gradient giúp làm sạch mảng tích lũy như thế nào.
```
