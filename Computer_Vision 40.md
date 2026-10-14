**Tài liệu bổ trợ** 

Bài tập lớn hợp nhất — Toán tử điểm, toán tử lân cận và phép biến đổi affine CLAHE • Ngưỡng thích nghi bằng ảnh tích phân • Hough đa tỉ lệ 

Môn Thị giác máy tính — Mã môn 121036   
Trường Đại học Giao thông vận tải TP.HCM 

**Tài liệu này dùng để làm gì?** 

Ba kỹ thuật trình bày ở đây *không được giảng chi tiết trên lớp*. Chúng nằm vừa đúng một bước bên ngoài nội dung bài giảng: mỗi kỹ thuật chỉ dùng những viên gạch các em đã có (bảng tra LUT, tích chập, nội suy song tuyến, tổng tích lũy, không gian tham số Hough), nhưng ghép lại theo một cách mà bài giảng chưa nói tới. Tài liệu cung cấp **đủ lý thuyết để tự cài đặt**, **đặc tả hàm cần nộp**, **yêu cầu thí nghiệm minh họa** và **danh sách lỗi thường gặp**. 

Mỗi kỹ thuật gồm hai phần nộp: **phần cài đặt** (tự viết, *không* dùng AI) và **phần thí nghiệm** (được dùng AI hỗ trợ, kèm prompt). Xem mục 5.1. 

Tài liệu này *không* phải là Giải pháp. Không có đoạn mã hoàn chỉnh nào ở đây. 

**Mục lục** 

**1 Vì sao là ba kỹ thuật này? 2** 

**2 Kỹ thuật 1 — CLAHE: Cân bằng lược đồ xám thích nghi có giới hạn tương phản 3** 2.1 Xuất phát điểm: cân bằng lược đồ xám toàn cục . . . . . . . . . . . . . . . . . . . 3 2.2 Hai chỗ HE toàn cục thất bại . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3 2.3 Giải pháp cho thất bại 2: cắt và phân phối lại lược đồ . . . . . . . . . . . . . . . . 3 2.4 Giải pháp cho thất bại 1: chia ô và nội suy bảng tra . . . . . . . . . . . . . . . . . 4 2.5 Đặc tả cài đặt . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5 2.6 Thí nghiệm minh họa . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5 

**3 Kỹ thuật 2 — Ngưỡng thích nghi bằng ảnh tích phân 6** 3.1 Ảnh tích phân: định nghĩa và truy vấn *O*(1) . . . . . . . . . . . . . . . . . . . . . . 6 3.2 Ngưỡng Bradley–Roth . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6 3.3 Mở rộng Sauvola: thêm phương sai cục bộ . . . . . . . . . . . . . . . . . . . . . . . 7 3.4 Điều đáng chú ý nhất: độ phức tạp không phụ thuộc cửa sổ . . . . . . . . . . . . 7 3.5 Đặc tả cài đặt . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8 3.6 Thí nghiệm minh họa . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8 

**4 Kỹ thuật 3 — Biến đổi Hough đa tỉ lệ 9** 4.1 Nhắc lại và đặt vấn đề . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9 4.2 Vì sao không tồn tại một độ phân giải đúng . . . . . . . . . . . . . . . . . . . . . . 9 4.3 Giải pháp 1: thô đến mịn (coarse-to-fine) . . . . . . . . . . . . . . . . . . . . . . . . 9 4.4 Giải pháp 2: bỏ phiếu theo hướng gradient . . . . . . . . . . . . . . . . . . . . . . 10 4.5 Giải pháp 3: mảng tích lũy cũng là một ảnh . . . . . . . . . . . . . . . . . . . . . . 10 4.6 Đặc tả cài đặt . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11 4.7 Thí nghiệm minh họa . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11 

**5 Ba kỹ thuật, một mô thức 13** 5.1 Quy định về việc dùng công cụ AI . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13 

**Tài liệu tham khảo gợi ý 14**  
**1 Vì sao là ba kỹ thuật này?** 

Ba kỹ thuật trình bày trong tài liệu này là ba bài tập cài đặt độc lập. Chúng không phụ thuộc lẫn nhau và có thể làm theo thứ tự bất kỳ. 

Điểm chung của cả ba là mỗi kỹ thuật *phá vỡ một ranh giới* mà bài giảng đã dựng lên: 

• **CLAHE** bắt đầu như một toán tử điểm (bảng tra LUT), nhưng khi bắt nó thích nghi theo vùng, nó *biến thành* một toán tử lân cận. Ranh giới “điểm và lân cận là hai loại khác nhau” sụp đổ. 

• **Ngưỡng thích nghi** là một toán tử điểm mà *tham số* của nó đến từ một toán tử lân cận. Nhờ ảnh tích phân, toán tử lân cận này chạy trong *O*(1) mỗi điểm ảnh, bất kể cửa sổ to bao nhiêu. Ranh giới “cửa sổ càng lớn càng chậm” sụp đổ. 

• **Hough đa tỉ lệ** nhắc ta rằng mảng tích lũy Hough *cũng là một ảnh*. Mọi toán tử các em viết ở Phần A đều dùng lại được trên nó: làm mượt bằng tích chập, tìm đỉnh bằng lọc cực đại địa phương, lọc nhiễu bằng ngưỡng. Ranh giới “ảnh và không gian tham số là hai thế giới khác nhau” sụp đổ. 

**Một câu hỏi xuyên suốt tài liệu** 

Cả ba kỹ thuật đều là câu trả lời cho cùng một câu hỏi: *làm sao để một quyết định toàn cục (một ngưỡng, một bảng tra, một ô lượng tử hóa) trở nên thích nghi với vị trí, mà không phải trả giá bằng thời gian tính toán?* Ba câu trả lời khác nhau cho cùng một câu hỏi. 

**Quy ước ký hiệu dùng chung** 

**Ký hiệu Ý nghĩa** 

*I*(*x, y*) Ảnh xám đầu vào, *x* là cột, *y* là hàng 

*H, W* Số hàng, số cột của ảnh 

*L* Số mức xám (thường *L* \= 256\) 

*h*\[*k*\] Lược đồ xám (histogram), *k* \= 0*, . . . , L −* 1 

*c*\[*k*\] Lược đồ tích lũy (CDF) đã chuẩn hóa 

*T*\[*·*\] Bảng tra (LUT), ánh xạ mức xám *→* mức xám 

*S*(*x, y*) Ảnh tích phân (summed-area table) 

(*ρ, θ*) Tham số đường thẳng trong không gian Hough 

*A*\[*i, j* \] Mảng tích lũy Hough 

**Quy ước chỉ số:** trong toàn bộ tài liệu, ảnh được lưu dạng numpy với thứ tự I\[y, x\] (hàng trước, cột sau). Mọi công thức toán viết theo (*x, y*); khi cài đặt phải đảo lại. Đây là nguồn lỗi phổ biến nhất của bài tập này. 

2  
**2 Kỹ thuật 1 — CLAHE: Cân bằng lược đồ xám thích nghi có giới hạn tương phản** 

**2.1 Xuất phát điểm: cân bằng lược đồ xám toàn cục** 

Bài giảng đã trình bày cân bằng lược đồ xám (Histogram Equalization, HE). Nhắc lại ngắn gọn dưới dạng *toán tử điểm*: ta xây một bảng tra duy nhất cho toàn ảnh,   
*T*\[*k*\] \= round\[(*L −* 1\) *· c*\[*k*\]\] *, c*\[*k*\] \= 1*N*∑*k j*\=0 

rồi áp dụng *I*out(*x, y*) \= *T*\[*I*(*x, y*)\]. 

*h*\[*j*\]*, N* \= *H · W,* (1) 

Điểm mấu chốt các em cần giữ trong đầu suốt phần này: **toàn bộ HE nằm gọn trong một mảng 256 phần tử**. Ảnh đầu vào chỉ tham gia vào việc *đếm*. Mọi thứ ta sẽ làm tiếp theo đều là thao tác trên những mảng 256 phần tử ấy, chứ không phải trên ảnh. 

**2.2 Hai chỗ HE toàn cục thất bại** 

**Thất bại 1 — ánh sáng không đều.** Giả sử ảnh chụp một nhãn container: nửa trái nằm dưới nắng, nửa phải trong bóng. Lược đồ xám toàn cục có hai cụm. Một bảng tra duy nhất phải phục vụ đồng thời cả hai cụm, nên nó kéo giãn khoảng giữa (vốn gần như trống) và nén cả hai cụm lại. Kết quả: không vùng nào được cải thiện. 

**Thất bại 2 — khuếch đại nhiễu.** Xét một vùng phẳng, gần như đồng nhất, chẳng hạn nền kim loại sạch. Trong vùng đó, toàn bộ điểm ảnh tập trung ở vài mức xám. CDF ở những mức ấy dốc đứng. Đạo hàm của bảng tra chính là độ dốc CDF, mà độ dốc CDF tại mức *k* tỉ lệ với *h*\[*k*\]: 

∆*k*\= (*L −* 1\) *h*\[*k*\]   
∆*T*\[*k*\]   
*N.* (2) 

Vậy **cột lược đồ càng cao thì độ tương phản tại mức xám đó càng bị kéo giãn**. Nhiễu *±*1 mức xám trong vùng phẳng sẽ bị biến thành chênh lệch hàng chục mức. Đây chính là lý do HE làm ảnh trông “rỗ”. 

**Hai vấn đề, hai Giải pháp độc lập** 

Thất bại 1 là vấn đề *không gian*: cần bảng tra khác nhau ở vị trí khác nhau *⇒* chia ô (tiling), sinh ra AHE. 

Thất bại 2 là vấn đề *biên độ*: cần chặn độ dốc bảng tra *⇒* giới hạn tương phản (contrast limiting), chữ “CL” trong CLAHE. 

Hai Giải pháp hoàn toàn độc lập. Hãy cài đặt và kiểm thử riêng từng cái trước khi ghép. 

**2.3 Giải pháp cho thất bại 2: cắt và phân phối lại lược đồ** 

Theo (2), muốn chặn độ dốc bảng tra tại một giá trị tối đa *s*max, ta chỉ cần chặn chiều cao lược đồ. Đặt **ngưỡng cắt** (clip limit) *β*. Thuật toán: 

1\. Với mỗi *k*, nếu *h*\[*k*\] *\> β*: ghi nhận phần dư *ek* \= *h*\[*k*\] *− β* rồi đặt *h*\[*k*\] *← β*. 2\. Cộng tổng phần dư *E* \=∑*kek*. 

3  
3\. Phân phối *E* đều lại cho toàn bộ *L* mức: *h*\[*k*\] *← h*\[*k*\] \+ *⌊E*/*L⌋*. 

Việc phân phối lại là *bắt buộc*, không phải tùy chọn: nếu chỉ cắt mà không trả lại, tổng ∑*kh*\[*k*\] không còn bằng *N*, CDF không đạt tới 1, và bảng tra sẽ không phủ hết dải sáng. 

**Chọn** *β* **như thế nào.** Nếu ta muốn độ dốc bảng tra không vượt quá *s*max lần độ dốc của phép biến đổi đồng nhất, thì từ (2) với *N*tile là số điểm trong một ô: 

*β* \=*N*tile *L*   
\[   
1 \+*α*100(*s*max *−* 1\)\]*, α ∈* \[0*,* 100\]*.* (3) 

Khi *α* \= 0, *β* \= *N*tile/*L*: lược đồ bị san phẳng hoàn toàn, ảnh ra *≈* ảnh gốc. Khi *α* \= 100 và *s*max lớn, không cột nào bị cắt: ta quay về AHE thuần túy. Hai giới hạn này là cách nhanh nhất để phát hiện lỗi trong phần cắt lược đồ. 

Trong thực tế, thư viện thường tham số hóa trực tiếp bằng clipLimit \= *s*max. Các em có thể chọn cách nào cũng được, miễn là ghi rõ công thức đã dùng trong chú thích của hàm. 

**2.4 Giải pháp cho thất bại 1: chia ô và nội suy bảng tra** 

Chia ảnh thành lưới *Gy × Gx* ô (mặc định 8 *×* 8). Với mỗi ô, tính lược đồ, cắt theo (3), rồi dựng bảng tra riêng *T*(*i,j*)\[*·*\] theo (1). Đến đây ta có *Gy ·Gx* bảng tra, mỗi bảng 256 phần tử. 

Nếu áp bảng tra của ô nào cho đúng ô ấy, kết quả sẽ có **đường ranh giới ô rõ rệt** — ảnh trông như bị chia ô vuông. Lý do: hai điểm ảnh cạnh nhau nhưng thuộc hai ô khác nhau được ánh xạ bằng hai hàm khác nhau. 

**Ý tưởng** Coi mỗi bảng tra là một “mẫu” đặt tại *tâm ô*. Với một điểm ảnh bất kỳ, ta nội suy song tuyến giữa bốn bảng tra của bốn tâm ô lân cận. 

*T*10 *T*11 

*p* 

*b*   
*T*00 *T*01 *~~a~~* 1 *− a* 

Với *a, b ∈* \[0*,* 1\] là tọa độ tương đối của *p* trong hình chữ nhật nối bốn tâm ô, giá trị ra là 

*I*out(*p*) \= (1 *− b*)   
\[   
(1 *− a*) *T*00\[*v*\] \+ *a T*01\[*v*\]   
\]   
\+ *b*   
\[   
(1 *− a*) *T*10\[*v*\] \+ *a T*11\[*v*\]   
\]   
*, v* \= *I*(*p*)*.* (4) 

**Sai lầm nghiêm trọng nhất của phần này** 

Rất nhiều cài đặt sai theo kiểu: *áp từng bảng tra cho toàn ảnh, tạo ra Gy · Gx ảnh, rồi nội suy song tuyến giữa các ảnh đó*. Kết quả *tình cờ* gần đúng nhưng tốn bộ nhớ gấp 64 lần và sai ở biên. Phải nội suy **giá trị bảng tra**, tức bốn số vô hướng *Tij* \[*v*\], chứ không phải bốn ảnh. Đây là điểm chấm điểm cứng. 

4  
**Xử lý biên.** Điểm ảnh nằm ngoài lưới tâm ô (viền ngoài rộng nửa ô) không có đủ bốn hàng xóm: 

• **Bốn góc ảnh:** chỉ có 1 bảng tra *⇒* áp trực tiếp, không nội suy. • **Bốn cạnh ảnh:** chỉ có 2 bảng tra *⇒* nội suy tuyến tính 1 chiều. • **Phần trong:** nội suy song tuyến đầy đủ theo (4).   
Một mẹo cài đặt gọn: thay vì viết ba nhánh, hãy *kẹp* (clamp) chỉ số ô về biên hợp lệ. Khi *p* nằm ngoài, chỉ số ô trái và phải trùng nhau, trọng số *a* tự động trở nên vô nghĩa nhưng kết quả vẫn đúng vì *T*00 \= *T*01. Cách này cho một nhánh duy nhất cho cả ba trường hợp. 

**2.5 Đặc tả cài đặt** 

**Hàm phải nộp — Kỹ thuật 1** 

def clip\_histogram(hist, clip\_limit): 

"""Cắt và phân phối lại lược đồ. 

hist: mảng (L,) số nguyên. Trả về mảng (L,) đã cắt, tổng không đổi.""" 

def build\_tile\_luts(img, grid=(8, 8), clip\_limit=2.0): 

"""Trả về mảng (Gy, Gx, L) uint8: bảng tra của từng ô.""" 

def clahe(img, grid=(8, 8), clip\_limit=2.0): 

"""CLAHE đầy đủ. img: (H, W) uint8. Trả về (H, W) uint8.""" 

**Thư viện được dùng:** numpy (kể cả np.cumsum, np.bincount, np.histogram), matplotlib để vẽ. 

**Cấm:** cv2.createCLAHE, cv2.equalizeHist, skimage.exposure.equalize\_adapthist, scipy.ndimage.map\_coordinates. Chỉ được gọi các hàm này trong *ô đối chiếu* có ghi chú rõ. 

**2.6 Thí nghiệm minh họa** 

**Yêu cầu — Kỹ thuật 1** 

Áp dụng cài đặt của mình lên một ảnh hoặc một bộ ảnh, và trình bày **cả hai** nội dung sau trong notebook: 

**(a) Ảnh hưởng của tham số.** Quét clip\_limit và grid qua ít nhất bốn giá trị mỗi tham số, trình bày dạng lưới ảnh. Hãy chọn ảnh sao cho hiệu ứng *nhìn thấy được*: clip\_limit chỉ lộ tác dụng trên ảnh có vùng phẳng nhiều nhiễu; grid chỉ lộ tác dụng trên ảnh có ánh sáng không đều theo vùng. 

**(b) So sánh với thuật toán đã học.** Đặt cạnh nhau, trên cùng một ảnh: kéo giãn tương phản tuyến tính, hiệu chỉnh gamma, cân bằng lược đồ xám toàn cục, và CLAHE. Kèm lược đồ xám của từng kết quả. Chỉ ra một ảnh mà CLAHE thắng rõ rệt, và — quan trọng hơn — **một ảnh mà CLAHE thua** một trong ba cách kia. 

5  
**3 Kỹ thuật 2 — Ngưỡng thích nghi bằng ảnh tích phân** 

**3.1 Ảnh tích phân: định nghĩa và truy vấn** *O*(1) 

**Ảnh tích phân** (summed-area table) *S* của ảnh *I* được định nghĩa   
*S*(*x, y*) \= ∑ *x′≤x*   
∑ *y′≤y* 

*I*(*x′, y′*)*.* (5) 

Tính trực tiếp theo định nghĩa mất *O*(*HW · HW*). Nhưng có một truy hồi hai chiều: *S*(*x, y*) \= *I*(*x, y*) \+ *S*(*x −* 1*, y*) \+ *S*(*x, y −* 1\) *− S*(*x −* 1*, y −* 1\)*,* (6) 

cho phép dựng toàn bộ bảng trong *một lượt quét*, *O*(*HW*). Số hạng trừ bù cho phần chồng lấn đã cộng hai lần — đây chính là nguyên lý bao hàm–loại trừ. 

**Truy vấn tổng chữ nhật.** Với hình chữ nhật có góc trên-trái (*x*1*, y*1) và góc dưới phải (*x*2*, y*2) (bao gồm cả biên): 

Σ \= *S*(*x*2*, y*2) *− S*(*x*1 *−* 1*, y*2) *− S*(*x*2*, y*1 *−* 1\) \+ *S*(*x*1 *−* 1*, y*1 *−* 1\)*.* (7) 

gốc (0*,* 0\) 

**Đệm viền là bắt buộc** 

*A B* Σ 

*C D* 

Σ \= *D − B − C* \+ *A* (bốn lần truy cập bộ nhớ, độc lập kích thước cửa sổ) 

Công thức (7) truy cập chỉ số *−*1\. **Đừng** xử lý bằng lệnh if. Hãy dựng *S* với kích thước (*H* \+ 1\) *×* (*W* \+ 1), hàng 0 và cột 0 toàn số không. Khi đó công thức trở thành thuần chỉ số dương và toàn bộ hàm truy vấn vectơ hóa được bằng lát cắt numpy. 

**Tràn số** 

Với ảnh uint8 kích thước 2000*×*3000, tổng lớn nhất là 255*·*6*×*106 *≈* 1*.*5*×*109 — vượt int32 khi cộng bình phương. Luôn ép kiểu sang np.int64 hoặc np.float64 *trước* khi cumsum. Bảng tích phân của *bình phương* tràn int32 rất nhanh: 2552*·* 6*×*106 *≈* 3*.*9 *×* 1011. 

**3.2 Ngưỡng Bradley–Roth** 

Ý tưởng: thay vì một ngưỡng toàn cục *T*, dùng ngưỡng phụ thuộc vị trí, lấy từ trung bình cục bộ trong cửa sổ *w × w* quanh điểm ảnh: 

*T*(*x, y*) \= *m*(*x, y*) *·*(1 *− t*)*, m*(*x, y*) \= 1*w*2Σ*w*(*x, y*)*,* (8) với *t ≈* 0*.*15 là hệ số lệch. Điểm ảnh được gán nền trước (foreground) nếu *I*(*x, y*) *\< T*(*x, y*).   
Diễn giải: mỗi điểm ảnh được so sánh với *hàng xóm của chính nó*, không phải với toàn ảnh. Vùng tối sẽ có *m* nhỏ, nên ngưỡng cũng nhỏ; chữ tối trên nền tối vẫn tách được. Đây chính xác là điều Otsu toàn cục không làm được. 

6  
**Đây là toán tử gì?** 

Phép so sánh *I \< T* là toán tử điểm. Nhưng *T* đến từ trung bình cửa sổ, tức toán tử lân cận. Vậy ngưỡng thích nghi là *một toán tử điểm có tham số sinh bởi toán tử lân cận* — cùng một kiến trúc với bộ lọc song phương (trọng số \= tích của nhân không gian và nhân giá trị) và với CLAHE (bảng tra \= hàm của lược đồ cục bộ). Ba ví dụ, một mô thức. 

**3.3 Mở rộng Sauvola: thêm phương sai cục bộ** 

Bradley–Roth thất bại ở vùng *hoàn toàn phẳng*: nếu cửa sổ chỉ chứa nền, trung bình *≈* giá trị nền, và ngưỡng *m*(1*−t*) nằm ngay dưới nó, nên nhiễu bị nhị phân hóa thành các đốm. Sauvola sửa lỗi này bằng cách đưa *độ lệch chuẩn cục bộ s*(*x, y*) vào: 

*T*(*x, y*) \= *m*(*x, y*)   
\[ 

1 \+ *κ*   
(*s*(*x, y*)   
*R−* 1   
)\] 

*, κ ≈* 0*.*34*, R* \= 128*.* (9) 

Khi *s →* 0 (vùng phẳng), *T → m*(1 *− κ*), hạ ngưỡng xuống *thấp hơn* trung bình khá nhiều, nên nhiễu không vượt ngưỡng. Khi *s* lớn (có chữ), *T → m*, giữ độ nhạy. Để tính *s* trong *O*(1), cần *hai* ảnh tích phân: *S*1 của *I* và *S*2 của *I*2. Khi đó   
(   
*s*2(*x, y*) \= Σ(2)   
*w*   
*w*2*−* 

**Mất chính xác do triệt tiêu** 

Σ(1)   
*w*   
*w*2   
)2 

*.* (10) 

Công thức (10) là hiệu của hai số lớn gần bằng nhau. Với ảnh gần đồng nhất, kết quả có thể ra *âm* do sai số dấu phẩy động, và np.sqrt trả về nan. Luôn kẹp: var \= np.maximum(var, 0.0). Dòng này trông thừa cho tới lần đầu tiên nó cứu các em khỏi một ảnh đầy nan. 

**3.4 Điều đáng chú ý nhất: độ phức tạp không phụ thuộc cửa sổ** Có ba cách tính trung bình cục bộ với bán kính cửa sổ *r*: 

**Cách làm Chi phí / điểm ảnh Ghi chú** 

Tích chập trực tiếp với nhân hộp *O*(*r*2) Dùng chính hàm convolve2d đã viết Tích chập tách được (hai nhân 1 chiều) *O*(*r*) Nhân hộp là tích của hai nhân 1 chiều Ảnh tích phân *O*(1) Bốn lần truy cập bộ nhớ, bất kể *r* 

Đo thời gian chạy của ba cách với *r ∈ {*1*,* 2*,* 4*,* 8*,* 16*,* 32*,* 64*}* và vẽ trên thang log: hai đường đầu dốc lên, đường thứ ba *nằm ngang*. Đường nằm ngang đó là toàn bộ thông điệp của kỹ thuật này. Nếu đường ảnh tích phân của các em không nằm ngang, gần như chắc chắn còn sót một vòng lặp Python theo điểm ảnh ở đâu đó. 

**Câu hỏi nối sang Phần A** 

Ba bộ lọc hộp liên tiếp xấp xỉ rất tốt một Gauss (hệ quả của định lý giới hạn trung tâm). Hãy đo sai số của xấp xỉ đó so với Gauss thật, rồi thay bước làm 

7  
mượt trong Canny bằng nó. Sai số định vị biên thay đổi bao nhiêu? Ở giá trị *σ* nào thì sai số ngừng có ý nghĩa? 

**3.5 Đặc tả cài đặt** 

**Hàm phải nộp — Kỹ thuật 2** 

def integral\_image(img): 

"""Trả về S kích thước (H+1, W+1), dtype int64, hàng/cột 0 bằng 0.""" 

def box\_sum(S, y1, x1, y2, x2): 

"""Tổng vùng \[y1..y2, x1..x2\] (bao gồm biên), vectơ hóa được.""" 

def local\_mean\_std(img, radius): 

"""Trả về (mean, std), mỗi cái (H, W) float64. Dùng 2 ảnh tích phân.""" 

def adaptive\_threshold(img, radius=15, method='bradley', t=0.15, k=0.34): """Trả về ảnh nhị phân (H, W) uint8 với giá trị 0 / 255.""" 

**Thư viện được dùng:** numpy (kể cả np.cumsum), time/timeit, matplotlib. **Cấm:** cv2.integral, cv2.adaptiveThreshold, cv2.boxFilter, cv2.blur, scipy.ndimage.uniform\_filter, skimage.filters.threshold\_sauvola. Chỉ dùng trong ô đối chiếu. 

**3.6 Thí nghiệm minh họa** 

**Yêu cầu — Kỹ thuật 2** 

**(a) Ảnh hưởng của tham số.** Quét radius qua ít nhất năm giá trị và t (hoặc k) qua ít nhất ba giá trị. Hai hiện tượng phải xuất hiện được trong lưới ảnh: radius quá nhỏ thì nét chữ dày bị rỗng ruột; radius quá lớn thì phương pháp thoái hóa dần về ngưỡng toàn cục. Chỉ ra vùng giá trị hợp lý và giải thích nó phụ thuộc vào cái gì trong ảnh. 

**(b) So sánh với thuật toán đã học.** Trên cùng ảnh: ngưỡng cố định thủ công, ngưỡng Otsu toàn cục, Bradley–Roth, và Sauvola. Ảnh dùng để so sánh *phải* có ánh sáng không đều — trên ảnh chiếu sáng đều, cả bốn cho kết quả gần như nhau và phép so sánh trở nên vô nghĩa. Bổ sung một ảnh có vùng nền phẳng rộng để cho thấy chỗ Sauvola hơn hẳn Bradley–Roth. 

**(c) Đường cong thời gian.** Ba đường theo bảng ở mục 3.4, trục *y* thang log. 8  
**4 Kỹ thuật 3 — Biến đổi Hough đa tỉ lệ** 

**4.1 Nhắc lại và đặt vấn đề** 

Bài giảng đã trình bày Hough chuẩn tắc: mỗi điểm biên (*x, y*) bỏ phiếu cho mọi đường thẳng đi qua nó, tham số hóa bởi 

*ρ* \= *x* cos *θ* \+ *y* sin *θ, θ ∈* \[0*, π*)*, ρ ∈* \[*−D, D*\]*, D* \=√*H*2 \+ *W*2*.* (11) 

Mảng tích lũy *A* được rời rạc hóa với bước ∆*ρ* và ∆*θ*. 

Câu hỏi cốt lõi mà bài giảng bỏ ngỏ: **chọn** ∆*ρ,* ∆*θ* **bằng bao nhiêu?** 

**4.2 Vì sao không tồn tại một độ phân giải đúng** 

Xét một đoạn thẳng thật, dài *ℓ* điểm ảnh, tâm ở gốc tọa độ. Nếu ta ước lượng góc sai một lượng *δθ*, thì đầu mút của đoạn bị dịch khỏi đường ước lượng một khoảng 

*d*max *≈ℓ*2*δθ.* (12) 

Để mọi điểm của đoạn vẫn rơi vào cùng một ô tích lũy, ta cần *d*max ≲ ∆*ρ*, tức 

| ∆*θ* ≲2 ∆*ρ ℓ* |
| :---- |

Đọc (13) cho kỹ, vì nó là toàn bộ lý do của phần này: 

(13) 

• **Đoạn dài cần** ∆*θ* **rất mịn.** Với *ℓ* \= 500 và ∆*ρ* \= 1, ta cần ∆*θ* ≲ 0*.*004 rad *≈* 0*.*23*◦*. 

• **Nhưng** ∆*θ* **mịn thì đoạn ngắn bị vỡ phiếu.** Một đoạn 30 điểm ảnh có nhiễu vị trí *±*1 điểm sẽ rải phiếu ra nhiều ô *θ* lân cận, không ô nào đủ cao để nổi lên thành đỉnh. 

• ∆*θ* **thô thì đoạn dài bị lệch.** Phiếu của một đoạn dài bị chẻ ra hai ô *ρ* kề nhau, đỉnh tù đi và vị trí đỉnh sai. 

Vậy *không có* một cặp (∆*ρ,* ∆*θ*) tốt cho mọi đoạn thẳng trong cùng một ảnh. Đây không phải chuyện tinh chỉnh tham số; đây là một mâu thuẫn cấu trúc. 

nhưng *θ* kém chính xác thô: đỉnh gọn   
đỉnh chìm trong nền mịn: phiếu bị rải   
**4.3 Giải pháp 1: thô đến mịn (coarse-to-fine)** 

Ý tưởng: đừng chọn một độ phân giải — dùng nhiều độ phân giải nối tiếp nhau. 

1\. Dựng mảng tích lũy *thô*, ví dụ ∆*θ*0 \= 1*◦*, ∆*ρ*0 \= 2 px. Ở độ phân giải này, đỉnh gọn và nổi rõ, dễ tìm. 

2\. Tìm *K* đỉnh ứng viên trong mảng thô. 

3\. Với mỗi ứng viên (*ρ∗, θ∗*), dựng lại một mảng tích lũy *nhỏ và mịn* chỉ phủ lân cận \[*ρ∗ ±* ∆*ρ*0*, θ∗ ±* ∆*θ*0\], với bước chia nhỏ đi *r* lần (ví dụ *r* \= 8). Chỉ những điểm biên đã bỏ phiếu cho ô thô mới tham gia bỏ phiếu lại. 

9  
4\. Lặp bước 3 thêm 1–2 tầng nếu cần. 

Chi phí: mảng mịn có kích thước cố định nhỏ (ví dụ 16 *×* 16\) và số điểm bỏ phiếu đã được lọc, nên tổng chi phí xấp xỉ chi phí một lần Hough thô. Nhưng độ chính xác góc đạt được là ∆*θ*0/*rn* sau *n* tầng — tức tinh hơn nhiều lần so với việc dựng thẳng một mảng mịn, mà lại không bị vỡ phiếu. 

**Bẫy quấn vòng ở** *θ* \= 0 **và** *θ* \= *π* 

Khi mở cửa sổ lân cận quanh *θ∗ ≈* 0, phần âm phải quấn về phía *π* — **và kèm theo đổi dấu** *ρ*. Từ (11), đường thẳng (*ρ, θ*) và (*−ρ, θ* \+ *π*) là *cùng một đường*. Cài đặt bỏ qua chi tiết này sẽ mất mọi đường gần thẳng đứng — đúng lúc mà mọi ảnh chụp chứng từ đều có cạnh gần thẳng đứng. Hãy viết một bài kiểm thử riêng cho trường hợp *θ ∈ {*0*.*5*◦,* 179*.*5*◦}*. 

**4.4 Giải pháp 2: bỏ phiếu theo hướng gradient** 

Hough chuẩn tắc lãng phí: một điểm biên bỏ phiếu cho *tất cả Nθ* giá trị góc, dù ta đã biết hướng của nó. Nhưng Canny (bước 1\) đã tính sẵn gradient (*gx, gy*) tại mọi điểm biên. Pháp tuyến của đường thẳng đi qua điểm đó chính là hướng gradient: 

*θg* \= atan2(*gy, gx*) mod *π.* (14) 

Vậy chỉ cần bỏ phiếu cho *θ ∈* \[*θg − δ, θg* \+ *δ*\], với *δ* khoảng 5*◦*–15*◦* để dung sai nhiễu gradient. Số phiếu mỗi điểm giảm từ *Nθ* xuống còn 2*δ*/∆*θ* — thường là giảm 10–20 lần. 

Lợi ích không chỉ là tốc độ: nền của mảng tích lũy *sạch hẳn*, vì phiếu rác (phiếu cho những góc vô lý) biến mất. Tỉ số đỉnh trên nền tăng mạnh, và đó mới là điều làm bước tìm đỉnh trở nên dễ dàng. 

**Nhập nhằng dấu** 

*θg* và *θg* \+ *π* cho cùng một đường thẳng nhưng khác dấu *ρ*. Sau khi lấy mod *π*, phải bảo đảm *ρ* tính theo (11) vẫn nhất quán. Cách an toàn: luôn tính *ρ* trực tiếp từ (*x, y, θ*) sau khi đã chuẩn hóa *θ* về \[0*, π*), đừng suy ngược dấu. 

**4.5 Giải pháp 3: mảng tích lũy cũng là một ảnh** 

Đây là chỗ Phần A quay lại đầy đủ. Sau khi bỏ phiếu, *A* là một mảng 2 chiều — tức là một ảnh. Mọi toán tử các em đã viết đều áp dụng được: 

**Vấn đề trong** *A* **Toán tử Phần A Vì sao hiệu quả** 

Phiếu bị chẻ sang ô kề do lượng tử hóa 

Một đường thẳng sinh ra chùm đỉnh sát nhau   
Tích chập với nhân Gauss nhỏ (*σ ≈* 1 ô) 

Lọc cực đại địa phương (max filter) *→* triệt phi cực đại   
Gộp lại phiếu của cùng một đường thẳng thật 

Chỉ giữ đỉnh trội trong bán kính cho trước 

Nền phiếu rác Ngưỡng — có thể là ngưỡng *thích nghi* (Kỹ 

thuật 2\!) 

10  
Nền Hough không đồng đều theo *ρ*: ô *ρ* gần 0 nhận nhiều phiếu hơn   
**Một quan sát dễ bỏ qua** 

Nền của mảng tích lũy *không* đồng đều. Với ảnh chữ nhật, một đường thẳng đi gần tâm cắt qua ảnh với chiều dài lớn hơn đường thẳng đi gần góc, nên nhận được nhiều phiếu hơn *ngay cả khi cả hai đều không phải đường thẳng thật*. Vì vậy một ngưỡng toàn cục trên *A* thiên vị đường gần tâm. Ngưỡng thích nghi trên *A* — đúng hàm ở Kỹ thuật 2 — sửa được điều này. 

**4.6 Đặc tả cài đặt** 

**Hàm phải nộp — Kỹ thuật 3** 

def hough\_accumulate(edges, theta\_range, rho\_range, n\_theta, n\_rho, 

grad\_dir=None, delta\_deg=None): 

"""Bỏ phiếu vào mảng tích lũy. Nếu grad\_dir khác None, chỉ bỏ phiếu 

trong dải \+/- delta\_deg quanh hướng gradient. 

Trả về (A, thetas, rhos).""" 

def find\_peaks(A, n\_peaks, nms\_radius=3, smooth\_sigma=1.0): 

"""Làm mượt A bằng hàm tích chập của chính nhóm, triệt phi cực đại, 

trả về danh sách (rho, theta, votes) sắp giảm dần.""" 

def hough\_multiscale(edges, grad\_dir, n\_levels=2, refine\_factor=8, ...): """Hough thô-đến-mịn. Trả về danh sách (rho, theta) đã tinh chỉnh.""" 

**Thư viện được dùng:** numpy, hàm convolve2d do chính nhóm viết ở Phần A, matplotlib. 

**Cấm:** cv2.HoughLines, cv2.HoughLinesP, skimage.transform.hough\_line, skimage.transform.hough\_line\_peaks, scipy.signal.find\_peaks (áp cho mảng 2 chiều), scipy.ndimage.maximum\_filter. Chỉ dùng trong ô đối chiếu. 

**4.7 Thí nghiệm minh họa** 

11  
**Yêu cầu — Kỹ thuật 3** 

Kỹ thuật này là kỹ thuật duy nhất trong ba kỹ thuật cho phép tạo **ảnh có đáp án đúng tuyệt đối**: các em tự vẽ đường thẳng với (*ρ*0*, θ*0) đã biết. Hãy tận dụng — phần lớn thí nghiệm dưới đây nên chạy trên ảnh tổng hợp, rồi mới kiểm lại trên ảnh thật. 

**(a) Ảnh hưởng của tham số.** Quét ∆*θ* và ∆*ρ* qua ít nhất bốn giá trị. Trình bày *cả* mảng tích lũy (dưới dạng ảnh) *và* các đường thẳng phát hiện được. Mảng tích lũy là nơi hiện tượng vỡ phiếu nhìn thấy rõ nhất. Sau đó quét số tầng *n* và hệ số tinh chỉnh *r*, vẽ sai số góc theo *n*. 

**(b) So sánh với thuật toán đã học.** Trên cùng bộ ảnh: Hough chuẩn tắc ở độ phân giải thô, Hough chuẩn tắc ở độ phân giải mịn, và Hough đa tỉ lệ. So sánh theo ba chỉ số: sai số góc so với đáp án đúng, tỉ số đỉnh trên nền của mảng tích lũy, và thời gian chạy. Bổ sung một lần chạy bật/tắt bỏ phiếu theo hướng gradient trên cùng ảnh. 

**(c) Hai trường hợp bắt buộc có trong bộ ảnh:** một ảnh chứa đường gần thẳng đứng (*θ*0 quanh 0*◦* hoặc 179*◦*), và một ảnh chứa đồng thời đoạn thẳng rất dài và đoạn thẳng rất ngắn. Cả hai đều là chỗ Hough một tỉ lệ hỏng. 

12  
**5 Ba kỹ thuật, một mô thức** 

Ba kỹ thuật trong tài liệu này được phát biểu bằng ba ngôn ngữ khác nhau — lược đồ xám, tổng tích lũy, không gian tham số — nhưng chúng là ba biến thể của cùng một ý tưởng: 

**Kỹ thuật Quyết định toàn cục bị thay thế** 

CLAHE Một bảng tra duy nhất cho cả ảnh 

Ngưỡng thích nghi Một ngưỡng duy nhất cho cả ảnh   
**Thay bằng cái gì** 

Một bảng tra cho mỗi ô, nội suy song tuyến giữa chúng 

Một ngưỡng cho mỗi điểm ảnh, sinh từ thống kê cửa sổ tính trong *O*(1) 

Hough đa tỉ lệ Một cặp (∆*ρ,* ∆*θ*) duy nhất Nhiều độ phân giải nối tiếp, mỗi tầng chỉ tinh chỉnh vùng lân cận 

đỉnh của tầng trước 

Trong cả ba trường hợp, cái giá phải trả lẽ ra là thời gian tính toán — và trong cả ba trường hợp, cái giá ấy được né bằng một thủ thuật khác nhau: nội suy thay vì tính lại, bảng tích lũy thay vì quét cửa sổ, thô-đến-mịn thay vì mịn ngay từ đầu. 

**Câu hỏi để tự trả lời** 

Cả ba kỹ thuật đều là *toán tử điểm có tham số sinh bởi toán tử lân cận*. Bộ lọc song phương ở Phần A cũng vậy (trọng số \= tích của nhân không gian và nhân giá trị). Vậy còn phép biến đổi affine thì sao — có cách nào làm cho nó “thích nghi theo vị trí” theo đúng nghĩa này không, và khi đó nó còn là affine nữa không? 

**5.1 Quy định về việc dùng công cụ AI** 

Mỗi kỹ thuật gồm hai phần nộp, và quy định cho hai phần này **ngược nhau**. **Phần cài đặt Phần thí nghiệm minh họa**   
**Nội dung** Các hàm trong ô “Hàm phải nộp” 

**Công cụ AI Không được dùng** — kể cả để gợi ý, sửa lỗi 

hay giải thích mã 

**Ràng buộc** Tự viết hoàn toàn, chỉ dùng thư viện trong 

danh sách cho phép 

**Cách ghi prompt trong notebook**   
Chọn ảnh, dựng bộ ảnh, quét tham số, vẽ hình, so sánh với thuật toán đã học 

**Được dùng** — để sinh/chọn ảnh phù hợp và dựng khung thí nghiệm 

**Mọi prompt đã dùng phải được chép nguyên văn vào notebook**, ngay trên ô mã tương ứng. Notebook phải chạy từ đầu đến cuối. 

Trước mỗi ô mã có dùng AI hỗ trợ, chèn một ô markdown theo mẫu: 

\#\#\# Có dùng AI hỗ trợ 

Công cụ: \<tên công cụ, phiên bản nếu biết\> 

Mục đích: \<sinh ảnh thử / dựng vòng lặp quét tham số / vẽ lưới ảnh / ...\> 13  
Prompt: 

\> \<chép nguyên văn prompt đã dùng\> 

Đã sửa lại những gì: \<mô tả ngắn phần các em phải sửa để chạy đúng\> 

Ô mã nào không có ô markdown này được hiểu là do các em tự viết. Thí nghiệm dùng AI mà không khai báo prompt sẽ không được tính điểm cho phần đó. 

**Vì sao chia như vậy.** Phần cài đặt là chỗ duy nhất các em thực sự học được ba thuật toán này; nhờ người khác viết hộ thì phần học biến mất, và mã do AI sinh cho đúng ba bài này hỏng theo những kiểu rất đặc trưng, rất khó phát hiện nếu không hiểu thuật toán: 

• **CLAHE:** gần như luôn nội suy giữa các *ảnh* thay vì giữa các *bảng tra*, và gần như luôn bỏ bước phân phối lại phần dư sau khi cắt. 

• **Ảnh tích phân:** thường quên đệm viền, quên ép kiểu int64, và quên kẹp phương sai về không âm. 

• **Hough:** gần như luôn bỏ qua bẫy quấn vòng ở *θ* \= 0 và *θ* \= *π*, nên im lặng đánh mất mọi đường gần thẳng đứng. 

Cả ba lỗi trên đều cho ra ảnh *trông có vẻ đúng*. 

Phần thí nghiệm thì ngược lại: chỗ khó không nằm ở việc viết mã vẽ hình, mà ở việc *nghĩ ra thí nghiệm nào đáng làm và chọn ảnh nào làm hiện ra hiệu ứng*. Một bộ ảnh chọn sai khiến cả bốn thuật toán cho kết quả như nhau và phép so sánh thành vô nghĩa — không công cụ nào chọn hộ các em được điều đó, vì nó đòi hỏi hiểu thuật toán sẽ hỏng ở đâu. Đó chính là phần được chấm. 

**Tài liệu tham khảo gợi ý** 

1\. K. Zuiderveld, “Contrast Limited Adaptive Histogram Equalization,” in *Graphics Gems IV*, Academic Press, 1994, pp. 474–485. — Nguồn gốc của CLAHE, mô tả đầy đủ phần cắt lược đồ và nội suy. 

2\. S. M. Pizer et al., “Adaptive histogram equalization and its variations,” *Com puter Vision, Graphics, and Image Processing*, vol. 39, no. 3, pp. 355–368, 1987\. 

3\. F. C. Crow, “Summed-area tables for texture mapping,” *ACM SIGGRAPH Com puter Graphics*, vol. 18, no. 3, pp. 207–212, 1984\. — Bài báo giới thiệu ảnh tích phân. 

4\. D. Bradley and G. Roth, “Adaptive Thresholding Using the Integral Image,” *Jour nal of Graphics Tools*, vol. 12, no. 2, pp. 13–21, 2007\. 

5\. J. Sauvola and M. Pietikäinen, “Adaptive document image binarization,” *Pattern Recognition*, vol. 33, no. 2, pp. 225–236, 2000\. 

6\. J. Illingworth and J. Kittler, “The Adaptive Hough Transform,” *IEEE Transactions on Pattern Analysis and Machine Intelligence*, vol. 9, no. 5, pp. 690–698, 1987\. — Nguồn gốc của ý tưởng thô-đến-mịn trong không gian tham số. 

7\. R. Szeliski, *Computer Vision: Algorithms and Applications*, 2nd ed., Springer, 2022\. — Mục 3.1 (toán tử điểm), 3.3 (toán tử lân cận), 3.6 (biến đổi hình học), 7.4 (Hough). 

14