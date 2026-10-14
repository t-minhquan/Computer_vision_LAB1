import unittest
import numpy as np
import time
from src.integral_threshold import integral_image, box_sum, local_mean_std, adaptive_threshold

class TestIntegralThreshold(unittest.TestCase):
    def test_integral_image_and_box_sum(self):
        """Kiểm tra tính chính xác của ảnh tích phân và truy vấn box_sum."""
        np.random.seed(42)
        img = np.random.randint(0, 256, size=(50, 60), dtype=np.uint8)
        S = integral_image(img)
        
        # Kích thước phải là (H+1, W+1) và hàng 0, cột 0 bằng 0
        self.assertEqual(S.shape, (51, 61))
        self.assertEqual(S.dtype, np.int64)
        self.assertTrue(np.all(S[0, :] == 0))
        self.assertTrue(np.all(S[:, 0] == 0))
        
        # Kiểm tra tính đúng đắn của box_sum ngẫu nhiên so với sum trực tiếp
        for _ in range(20):
            y1 = np.random.randint(0, 40)
            y2 = np.random.randint(y1, 50)
            x1 = np.random.randint(0, 50)
            x2 = np.random.randint(x1, 60)
            
            expected = int(np.sum(img[y1:y2+1, x1:x2+1]))
            actual = int(box_sum(S, y1, x1, y2, x2))
            self.assertEqual(expected, actual, f"Lỗi box_sum tại vùng [{y1}..{y2}, {x1}..{x2}]")

    def test_no_nan_on_constant_image(self):
        """Kiểm tra không bị lỗi NaN khi tính Sauvola trên vùng hoàn toàn phẳng (var <= 0 do sai số float)."""
        img = np.full((100, 100), 120, dtype=np.uint8)
        mean, std = local_mean_std(img, radius=10)
        
        self.assertFalse(np.isnan(mean).any(), "Mean không được chứa NaN")
        self.assertFalse(np.isnan(std).any(), "Std không được chứa NaN (phải kẹp phương sai np.maximum(var, 0.0))")
        
        bin_sauvola = adaptive_threshold(img, radius=10, method='sauvola')
        self.assertEqual(bin_sauvola.shape, img.shape)
        self.assertFalse(np.isnan(bin_sauvola).any())

    def test_complexity_independence(self):
        """Kiểm tra thời gian chạy không phụ thuộc vào bán kính cửa sổ (O(1))."""
        img = np.random.randint(0, 256, size=(200, 200), dtype=np.uint8)
        
        t0 = time.time()
        local_mean_std(img, radius=2)
        t_small = time.time() - t0
        
        t0 = time.time()
        local_mean_std(img, radius=32)
        t_large = time.time() - t0
        
        # Cả 2 lần chạy O(1) chỉ chênh lệch rất nhỏ (cùng cấp số)
        # Thay vì tăng hàng trăm lần như tích chập trực tiếp O(r^2)
        self.assertLess(t_large, t_small * 5.0)

if __name__ == '__main__':
    unittest.main()
