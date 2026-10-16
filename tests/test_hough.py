import unittest
import numpy as np
from src.multiscale_hough import hough_accumulate, find_peaks, hough_multiscale, wrap_theta_rho, are_lines_duplicate


class TestMultiscaleHough(unittest.TestCase):
    def test_wrap_theta_rho(self):
        """Kiểm tra xử lý quấn vòng theta qua 0 và pi kèm đổi dấu rho (Mục 4.3)."""
        # theta = -0.1 rad -> quấn về pi - 0.1 rad, rho đổi dấu
        th_wrap, rh_wrap = wrap_theta_rho(-0.1, 50.0)
        self.assertAlmostEqual(th_wrap, np.pi - 0.1, places=5)
        self.assertAlmostEqual(rh_wrap, -50.0, places=5)
        
        # theta = pi + 0.1 rad -> quấn về 0.1 rad, rho đổi dấu
        th_wrap2, rh_wrap2 = wrap_theta_rho(np.pi + 0.1, 40.0)
        self.assertAlmostEqual(th_wrap2, 0.1, places=5)
        self.assertAlmostEqual(rh_wrap2, -40.0, places=5)

    def test_vertical_lines_wrap_around_trap(self):
        """
        Kiểm tra bài kiểm thử riêng theo yêu cầu Mục 4.3 (trang 10):
        'Hãy viết một bài kiểm thử riêng cho trường hợp theta in {0.5 độ, 179.5 độ}'.
        """
        h, w = 200, 200
        
        # 1. Kiểm tra đường thẳng có góc theta = 0.5 độ
        th_05 = np.radians(0.5)
        edges_05 = np.zeros((h, w), dtype=np.uint8)
        rho0_1 = 50.0
        for y in range(h):
            x = int(round((rho0_1 - y * np.sin(th_05)) / np.cos(th_05)))
            if 0 <= x < w:
                edges_05[y, x] = 255
                
        lines_05 = hough_multiscale(edges_05, n_levels=2, refine_factor=8, n_peaks=1)
        self.assertGreater(len(lines_05), 0)
        rho_est1, theta_est1 = lines_05[0]
        # Chênh lệch góc mod pi phải nhỏ hơn 1 độ (độ phân giải thô là 1 độ)
        diff_t1 = abs(theta_est1 - th_05)
        if diff_t1 > np.pi / 2.0:
            diff_t1 = np.pi - diff_t1
        self.assertLess(diff_t1, np.radians(1.0))

        # 2. Kiểm tra đường thẳng có góc theta = 179.5 độ
        th_1795 = np.radians(179.5)
        edges_1795 = np.zeros((h, w), dtype=np.uint8)
        rho0_2 = -50.0
        for y in range(h):
            x = int(round((rho0_2 - y * np.sin(th_1795)) / np.cos(th_1795)))
            if 0 <= x < w:
                edges_1795[y, x] = 255
                
        lines_1795 = hough_multiscale(edges_1795, n_levels=2, refine_factor=8, n_peaks=1)
        self.assertGreater(len(lines_1795), 0)
        rho_est2, theta_est2 = lines_1795[0]
        diff_t2 = abs(theta_est2 - th_1795)
        if diff_t2 > np.pi / 2.0:
            diff_t2 = np.pi - diff_t2
        self.assertLess(diff_t2, np.radians(1.0))

    def test_long_and_short_segments(self):
        """
        Kiểm tra ảnh chứa đồng thời đoạn rất dài (100 px) và đoạn rất ngắn (20 px) (Mục 4.7c).
        """
        h, w = 150, 150
        edges = np.zeros((h, w), dtype=np.uint8)
        # Đoạn dài tại x = 30
        edges[20:120, 30] = 255
        # Đoạn ngắn tại x = 90
        edges[60:80, 90] = 255
        
        lines = hough_multiscale(edges, n_levels=2, refine_factor=8, n_peaks=2)
        self.assertEqual(len(lines), 2)
        detected_rhos = sorted([abs(line[0]) for line in lines])
        self.assertAlmostEqual(detected_rhos[0], 30.0, delta=2.5)
        self.assertAlmostEqual(detected_rhos[1], 90.0, delta=2.5)


if __name__ == '__main__':
    unittest.main()
