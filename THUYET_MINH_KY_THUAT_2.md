# THUYẾT MINH KỸ THUẬT 2 — NGƯỠNG THÍCH NGHI BẰNG ẢNH TÍCH PHÂN

*Tài liệu gốc: Computer_Vision 40.pdf, chương 3, trang 6–8.*

## 1. Mục tiêu, mục đích

**Mục tiêu:** Nhị phân hóa ảnh có chiếu sáng không đều để tách chữ/vật thể tối khỏi nền sáng. Dùng ngưỡng **riêng cho từng pixel** thay vì dùng duy nhất một ngưỡng cho toàn ảnh.

**Mục đích của ảnh tích phân:** Tính tổng cường độ của bất kỳ cửa sổ chữ nhật nào bằng đúng 4 phép tra bảng. Do đó cửa sổ rộng hơn không làm tăng số phép cộng cho mỗi truy vấn.

## 2. Bản chất thuật toán (mục 3.1)

Ảnh trong NumPy có chỉ số `I[y,x]`: **y là hàng, x là cột**. Xây bảng tổng tích lũy có kích thước `(H+1,W+1)` và hàng/cột đầu bằng 0. Gọi `S[a,b]` là tổng của `I[0:a,0:b]` (theo lát cắt Python, không tính a và b).

Công thức tính tổng vùng **bao gồm hai đầu** `[y1..y2,x1..x2]`:

```text
sum = S[y2+1,x2+1] - S[y1,x2+1]
    - S[y2+1,x1]   + S[y1,x1]
```

Đây là nguyên lý **bao hàm–loại trừ**: cộng toàn bộ vùng D; trừ hai vùng không cần ở trên và bên trái; cộng lại phần giao đã trừ hai lần.

Ví dụ ảnh 3×3:

```text
1 2 3
4 5 6
7 8 9
```

- Tổng toàn ảnh = **45**.
- Tổng ô vuông hàng 1..2, cột 1..2 = **5+6+8+9 = 28**.

Bảng tích phân được tạo trong **O(HW)** và hàm `box_sum` tính mỗi cửa sổ trong **O(1)**. Trước khi `cumsum`, ép `int64` để tránh tràn số. Ảnh bình phương `I**2` cũng phải ép kiểu trước khi nhân.

## 3. Trung bình và độ lệch chuẩn (mục 3.3)

Với `radius=r`, cửa sổ bình thường rộng `2r+1`. Ở mép ảnh, cửa sổ bị cắt và phải chia cho **diện tích thực sự** chứ không luôn chia `(2r+1)^2`.

Hai bảng được dùng:

- `S1`: ảnh tích phân của `I`.
- `S2`: ảnh tích phân của `I²`.

Trung bình và độ lệch chuẩn cục bộ:

```text
mean = sum(I)/area
E2   = sum(I^2)/area
var  = max(E2 - mean^2, 0.0)
std  = sqrt(var)
```

`max(...,0)` ngăn `sqrt` của giá trị âm rất nhỏ do lỗi dấu phẩy động.

## 4. Bradley–Roth và Sauvola (mục 3.2, 3.3)

**Bradley–Roth:** `T = mean * (1 - t)`, mặc định `t=0.15`. Nếu `I[y,x] < T[y,x]` thì xem là chữ **đen (0)**, còn lại là nền **trắng (255)**.

**Sauvola:** `T = mean * (1 + k * (std/128 - 1))`, mặc định `k=0.34`. Kết hợp **mean** và **std**: vùng phẳng có std nhỏ → hạ ngưỡng, giảm chấm giả; vùng có chữ có độ biến thiên cao → tăng độ nhạy so với vùng phẳng.

Ví dụ dễ nhớ với `mean=120`, `std=10`: Bradley (t=0.15) cho `T=102`; Sauvola (k=0.34) cho xấp xỉ `T=82.38`. Đó là lý do Sauvola có thể tránh nhận nhầm nhiễu trong nền phẳng.

## 5. Thí nghiệm A — quét tham số (mục 3.6a)

- 7 `radius`: `1,3,7,15,31,127,511`.
- 3 `t`: `0.05,0.15,0.25` (Bradley–Roth).
- 3 `k`: `0.20,0.34,0.50` (Sauvola).

**Nhận xét:** r=1 chỉ nhìn được khác biệt sát đường biên của nét chữ, làm chữ rỗng bên trong. r khoảng **7–31 trên ảnh thử này** giúp giữ chữ rõ. r=511 vượt kích thước ảnh 240×460 nên cửa sổ nào cũng chứa toàn bộ ảnh: cùng `mean` → đúng ngưỡng toàn cục (với Bradley). Không có một `radius` tốt nhất cho mọi ảnh; cần cân nhắc độ dày chữ, kích cỡ ký tự và mức độ biến thiên của ánh sáng.

## 6. Thí nghiệm B — so sánh (mục 3.6b)

Bốn phương pháp trên **cùng ảnh**: (1) ngưỡng cố định 128, (2) Otsu toàn cục tự tính từ histogram, (3) Bradley–Roth r=15, t=0.15, (4) Sauvola r=15, k=0.34.

**Ảnh ánh sáng không đều:** Ngưỡng cố định và Otsu chọn một ngưỡng chung nên vùng tối nền dễ bị xem nhầm thành chữ. Bradley–Roth/Sauvola xử lý tốt hơn trên ảnh tổng hợp này vì ngưỡng thay đổi theo vị trí.

**Ảnh nền phẳng rộng có nhiễu:** Trong vùng nền trống được chọn, tỷ lệ pixel **nền → chữ giả**: Bradley–Roth **15.12%**, Sauvola **2.25%**. Điều này thể hiện lợi ích của std đối với nền tương đối phẳng. Kết quả **phụ thuộc bộ ảnh và độ nhiễu**; Otsu có thể cạnh tranh hoặc tốt hơn trên một vài ảnh riêng.

`B_chi_so_so_sanh.csv` có thêm Precision, Recall, F1 và số pixel nhận nhầm. Các chỉ số ở đây dựa trên mặt nạ chữ được sinh cùng ảnh tổng hợp, không phải nhãn của một tập dữ liệu ảnh thật.

## 7. Thí nghiệm C — 3 đường thời gian (mục 3.4, 3.6c)

Cùng ảnh 64×64; quét `radius` = `{1,2,4,8,16,32,64}`. Mỗi điểm đo 5 lần, lấy **median**, vẽ thời gian miligiây trên trục Y dạng **log**.

| Cách | Chi phí mỗi điểm ảnh theo r | Diễn giải |
|---|---|---|
| Tích chập trực tiếp | O(r²) | Cộng `(2r+1)²` pixel trong mỗi cửa sổ |
| Tích chập tách được | O(r) | Cộng ngang rồi dọc |
| Ảnh tích phân | O(1) | 4 lần tra bảng để tính tổng cửa sổ |

**Nhận xét:** Lúc r bé, overhead của NumPy có thể khiến cách ảnh tích phân không phải nhanh nhất. Khi r lớn, tích chập trực tiếp tốn thời gian hơn rõ rệt; tách được ở giữa; ảnh tích phân ít phụ thuộc r. Giá trị tuyệt đối thay đổi theo máy. Cả 3 cách đều đã được kiểm tra cho **cùng kết quả số** trong sai số dấu phẩy động.

## 8. Câu hỏi vấn đáp thường gặp

**Q1. Tại sao dùng ảnh tích phân?** Vì tổng của một hình chữ nhật có thể lấy với 4 chỉ số, không cần cộng lại hàng nghìn pixel khi r lớn.

**Q2. Tại sao cần hàng và cột số 0?** Để dùng đúng một công thức truy vấn cho cả vùng giáp biên trên/trái, không cần xử lý chỉ số âm bằng nhiều `if`.

**Q3. Tại sao phải dùng int64?** Tổng tích lũy của I² có thể vượt rất nhanh giới hạn `int32`. Nếu nhân ngay trong `uint8` thì sai ngay trước cả khi tính tổng.

**Q4. Bradley–Roth khác Sauvola ra sao?** Bradley chỉ dùng mean, Sauvola dùng mean và std. Sauvola thường ít nhận nhầm nền phẳng có nhiễu hơn trong trường hợp thử nghiệm phù hợp.

**Q5. Vì sao r quá nhỏ làm rỗng nét chữ?** Một pixel nằm sâu trong nét chữ có các hàng xóm cũng tối → mean cục bộ gần bằng giá trị pixel → `I < mean*(1-t)` sai → pixel chữ bị biến thành trắng.

**Q6. Vì sao r quá lớn giống ngưỡng toàn cục?** Vì mọi vị trí đều dùng toàn bộ ảnh làm cửa sổ → thống kê (mean, std) không còn thay đổi theo vị trí.

**Q7. Vì sao nói O(1) nhưng vẫn mất thời gian khi ảnh lớn?** O(1) tính cho một *truy vấn vùng* sau khi đã có bảng. Toàn bộ ảnh cần xây bảng O(HW), rồi chạy một truy vấn cho mỗi pixel, nên tổng O(HW).

**Q8. Tại sao dùng trục log ở thí nghiệm C?** Thời gian trực tiếp tại r lớn cao hơn nhiều so với r nhỏ; trục log giúp thấy cả 3 đường trên cùng biểu đồ.

**Q9. Những lỗi điển hình?** Nhầm x và y; thiếu đệm 0; tràn số; chia sai diện tích ở biên; không kẹp phương sai về ≥0; làm thí nghiệm trên ảnh đều sáng nên không thấy khác biệt.

**Q10. Liên hệ với kiến thức trong môn?** Ngưỡng hóa là toán tử điểm `I < T`, nhưng `T` được lấy từ vùng lân cận. Ảnh tích phân giúp tổng hợp thông tin lân cận nhanh và làm tham số ngưỡng **thích nghi theo vị trí**.

## 9. Kết luận

Kỹ thuật 2 giải quyết vấn đề **ngưỡng toàn cục không thích ứng với sự thay đổi chiếu sáng** bằng cách dùng thống kê cửa sổ tại từng pixel. Kết quả quan trọng nhất là tổng cửa sổ bằng ảnh tích phân có chi phí **O(1) cho mỗi pixel, không phụ thuộc r**. Các tình huống thử nghiệm cho thấy những điểm phương pháp có thể tốt lên hoặc thất bại; các nhận xét không thay thế đánh giá trên ảnh thực tế.
