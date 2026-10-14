import unittest
import numpy as np
from src.clahe import clip_histogram, build_tile_luts, clahe

class TestCLAHE(unittest.TestCase):
    def test_clip_histogram_conservation(self):
        """Kiểm tra tổng số điểm ảnh trước và sau khi clip_histogram phải bằng nhau tuyệt đối."""
        np.random.seed(42)
        # Tạo histogram giả lập có 1 vài cột rất cao
        hist = np.random.randint(0, 100, size=256)
        hist[50] = 5000
        hist[120] = 3000
        total_before = np.sum(hist)
        
        clipped = clip_histogram(hist, clip_limit=200)
        total_after = np.sum(clipped)
        
        self.assertEqual(total_before, total_after, "Tổng số lượng pixel phải được bảo toàn chính xác sau khi cắt và phân phối lại!")
        # Kiểm tra không có bin nào còn giữ nguyên giá trị ban đầu vượt trội nếu không được san phẳng
        self.assertLess(clipped[50], 5000)

    def test_clahe_output_range_and_shape(self):
        """Kiểm tra output của CLAHE giữ nguyên kích thước và dải mức xám uint8 [0, 255]."""
        np.random.seed(42)
        img = np.random.randint(0, 256, size=(128, 128), dtype=np.uint8)
        out = clahe(img, grid=(8, 8), clip_limit=2.0)
        
        self.assertEqual(out.shape, img.shape)
        self.assertEqual(out.dtype, np.uint8)
        self.assertTrue(np.all(out >= 0) and np.all(out <= 255))

    def test_clahe_uniform_image(self):
        """Ảnh hoàn toàn đồng nhất không bị lỗi chia 0 hay crash."""
        img = np.full((64, 64), 100, dtype=np.uint8)
        out = clahe(img, grid=(4, 4), clip_limit=2.0)
        self.assertEqual(out.shape, img.shape)

if __name__ == '__main__':
    unittest.main()
