import unittest
import numpy as np
from src.multiscale_hough import hough_accumulate, find_peaks, hough_multiscale, wrap_theta_rho

class TestMultiscaleHough(unittest.TestCase):
    def test_wrap_theta_rho(self):
        """Kiểm tra xử lý quấn vòng theta qua 0 và pi kèm đổi dấu rho."""
        # theta = -0.1 rad (~ -5.7 độ) -> tương đương pi - 0.1 rad, rho đổi dấu
        th_wrap, rh_wrap = wrap_theta_rho(-0.1, 50.0)
        self.assertAlmostEqual(th_wrap, np.pi - 0.1, places=5)
        self.assertAlmostEqual(rh_wrap, -50.0, places=5)
        
        # theta = pi + 0.1 rad -> tương đương 0.1 rad, rho đổi dấu
        th_wrap2, rh_wrap2 = wrap_theta_rho(np.pi + 0.1, 40.0)
        self.assertAlmostEqual(th_wrap2, 0.1, places=5)
        self.assertAlmostEqual(rh_wrap2, -40.0, places=5)

    def test_vertical_line_detection(self):
        """
        Kiểm tra phát hiện đường thẳng gần thẳng đứng (theta ~ 0 rad).
        Đảm bảo không bị mất do bẫy quấn vòng góc.
        """
        h, w = 100, 100
        edges = np.zeros((h, w), dtype=np.uint8)
        
        # Vẽ một đường thẳng đứng tại x = 30
        edges[:, 30] = 255
        
        # Đường thẳng x = 30 có theta = 0 rad, rho = 30
        lines = hough_multiscale(edges, n_levels=2, refine_factor=4, n_peaks=1)
        
        self.assertGreater(len(lines), 0, "Phải phát hiện được đường thẳng đứng!")
        rho_est, theta_est, votes = lines[0]
        
        # Theta ước lượng phải xấp xỉ 0 (hoặc rất gần pi do tính tương đương)
        diff_theta = min(abs(theta_est - 0.0), abs(theta_est - np.pi))
        self.assertLess(diff_theta, np.radians(2.0), f"Sai số góc quá lớn: {np.degrees(diff_theta)} độ")
        self.assertAlmostEqual(abs(rho_est), 30.0, delta=2.0)

    def test_horizontal_line_detection(self):
        """Kiểm tra phát hiện đường thẳng ngang tại y = 45 (theta = pi/2, rho = 45)."""
        h, w = 100, 100
        edges = np.zeros((h, w), dtype=np.uint8)
        edges[45, :] = 255
        
        lines = hough_multiscale(edges, n_levels=2, refine_factor=4, n_peaks=1)
        self.assertGreater(len(lines), 0)
        rho_est, theta_est, votes = lines[0]
        
        self.assertAlmostEqual(theta_est, np.pi / 2.0, delta=np.radians(2.0))
        self.assertAlmostEqual(abs(rho_est), 45.0, delta=2.0)

if __name__ == '__main__':
    unittest.main()
