"""Kiểm thử Kỹ thuật 2 - Computer_Vision 40.pdf, mục 3.5.

"""

import unittest
import numpy as np

from ky_thuat_2 import (
    integral_image, box_sum, local_mean_std, adaptive_threshold,
    local_mean_direct, local_mean_separable, local_mean_integral,
)


def mean_std_reference(img, radius):
    """Cách đối chiếu đơn giản: cắt cửa sổ thật, tính bằng NumPy."""
    h, w = img.shape
    mean = np.empty((h, w), dtype=np.float64)
    std = np.empty((h, w), dtype=np.float64)
    for y in range(h):
        for x in range(w):
            patch = img[max(0, y - radius):min(h, y + radius + 1),
                        max(0, x - radius):min(w, x + radius + 1)]
            mean[y, x] = patch.mean()
            std[y, x] = patch.astype(np.float64).std()
    return mean, std


class TestIntegralImage(unittest.TestCase):
    def test_kich_thuoc_dtype_dem_vien(self):
        img = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.uint8)
        S = integral_image(img)
        self.assertEqual(S.shape, (3, 4))
        self.assertEqual(S.dtype, np.dtype('int64'))
        self.assertTrue(np.all(S[0] == 0))
        self.assertTrue(np.all(S[:, 0] == 0))
        np.testing.assert_array_equal(S, [[0, 0, 0, 0],
                                          [0, 1, 3, 6],
                                          [0, 5, 12, 21]])

    def test_anh_mot_pixel_va_anh_khong(self):
        np.testing.assert_array_equal(integral_image(np.array([[255]], dtype=np.uint8)),
                                      [[0, 0], [0, 255]])
        img = np.zeros((4, 5), dtype=np.uint8)
        self.assertTrue(np.all(integral_image(img) == 0))

    def test_khong_tran_so_voi_binh_phuong(self):
        img = np.full((200, 300), 255, dtype=np.int64)
        S = integral_image(img ** 2)
        self.assertEqual(int(S[-1, -1]), 255 ** 2 * 200 * 300)
        self.assertGreater(int(S[-1, -1]), 2 ** 31 - 1)

    def test_anh_khong_phai_2d_bao_loi(self):
        with self.assertRaises(ValueError):
            integral_image(np.zeros((2, 3, 3), dtype=np.uint8))


class TestBoxSum(unittest.TestCase):
    def setUp(self):
        self.img = np.arange(1, 21, dtype=np.uint8).reshape(4, 5)
        self.S = integral_image(self.img)

    def test_tong_toan_anh_va_o_bien(self):
        self.assertEqual(int(box_sum(self.S, 0, 0, 3, 4)), 210)
        self.assertEqual(int(box_sum(self.S, 0, 0, 0, 0)), 1)
        self.assertEqual(int(box_sum(self.S, 3, 4, 3, 4)), 20)
        self.assertEqual(int(box_sum(self.S, 1, 1, 2, 3)), int(self.img[1:3, 1:4].sum()))

    def test_so_sanh_tong_voi_cat_mang(self):
        for y1 in range(4):
            for x1 in range(5):
                for y2 in range(y1, 4):
                    for x2 in range(x1, 5):
                        wanted = int(self.img[y1:y2+1, x1:x2+1].sum())
                        got = int(box_sum(self.S, y1, x1, y2, x2))
                        self.assertEqual(got, wanted)

    def test_vector_hoa_truy_van(self):
        y1 = np.array([0, 1, 3])
        x1 = np.array([0, 1, 4])
        y2 = np.array([3, 2, 3])
        x2 = np.array([4, 3, 4])
        got = box_sum(self.S, y1, x1, y2, x2)
        wanted = [int(self.img[a:b+1, c:d+1].sum())
                  for a, c, b, d in zip(y1, x1, y2, x2)]
        np.testing.assert_array_equal(got, wanted)


class TestLocalMeanStd(unittest.TestCase):
    def test_so_sanh_voi_cach_lam_truc_tiep(self):
        rng = np.random.default_rng(2026)
        img = rng.integers(0, 256, size=(8, 11), dtype=np.uint8)
        for radius in [0, 1, 2, 5, 20]:
            with self.subTest(radius=radius):
                mean, std = local_mean_std(img, radius)
                mean_ref, std_ref = mean_std_reference(img, radius)
                self.assertEqual(mean.shape, img.shape)
                self.assertEqual(std.shape, img.shape)
                self.assertEqual(mean.dtype, np.float64)
                self.assertEqual(std.dtype, np.float64)
                np.testing.assert_allclose(mean, mean_ref, atol=1e-10)
                np.testing.assert_allclose(std, std_ref, atol=1e-9)

    def test_vung_phang_khong_sinh_nan(self):
        img = np.full((20, 30), 160, dtype=np.uint8)
        for radius in [0, 1, 10, 100]:
            mean, std = local_mean_std(img, radius)
            self.assertTrue(np.isfinite(std).all())
            np.testing.assert_allclose(mean, 160)
            np.testing.assert_allclose(std, 0)

    def test_dau_vao_sai_bao_loi(self):
        img = np.ones((3, 3), dtype=np.uint8)
        for radius in [-1, 1.5, '3']:
            with self.subTest(radius=radius):
                with self.assertRaises(ValueError):
                    local_mean_std(img, radius)
        with self.assertRaises(ValueError):
            local_mean_std(img.astype(float), 1)


class TestAdaptiveThreshold(unittest.TestCase):
    def test_bradley_dung_cong_thuc(self):
        img = np.array([[70, 105, 115], [90, 180, 220], [35, 150, 245]], dtype=np.uint8)
        mean, _ = mean_std_reference(img, 1)
        expected = np.where(img < mean * (1 - 0.15), 0, 255).astype(np.uint8)
        np.testing.assert_array_equal(adaptive_threshold(img, 1, method='bradley', t=0.15), expected)

    def test_sauvola_dung_cong_thuc(self):
        img = np.array([[70, 105, 115], [90, 180, 220], [35, 150, 245]], dtype=np.uint8)
        mean, std = mean_std_reference(img, 1)
        T = mean * (1 + 0.34 * (std / 128 - 1))
        expected = np.where(img < T, 0, 255).astype(np.uint8)
        np.testing.assert_array_equal(adaptive_threshold(img, 1, method='sauvola', k=0.34), expected)

    def test_dau_ra_nhi_phan_va_kieu_du_lieu(self):
        img = np.array([[0, 30, 160], [220, 250, 255]], dtype=np.uint8)
        for method in ['bradley', 'sauvola']:
            with self.subTest(method=method):
                result = adaptive_threshold(img, method=method)
                self.assertEqual(result.dtype, np.uint8)
                self.assertEqual(result.shape, img.shape)
                self.assertTrue(set(np.unique(result)).issubset({0, 255}))

    def test_ban_kinh_lon_bang_nguong_trung_binh_toan_anh(self):
        img = np.arange(100, dtype=np.uint8).reshape(10, 10)
        result = adaptive_threshold(img, radius=1000, method='bradley', t=0.15)
        expected = np.where(img < img.mean() * 0.85, 0, 255).astype(np.uint8)
        np.testing.assert_array_equal(result, expected)

    def test_phuong_phap_sai_bao_loi(self):
        with self.assertRaises(ValueError):
            adaptive_threshold(np.ones((4, 4), dtype=np.uint8), method='khac')


class TestBaCachTinhMean(unittest.TestCase):
    def test_cung_ket_qua_voi_cac_ban_kinh(self):
        rng = np.random.default_rng(17)
        img = rng.integers(0, 256, size=(7, 9), dtype=np.uint8)
        for radius in [0, 1, 3, 10]:
            with self.subTest(radius=radius):
                ref, _ = mean_std_reference(img, radius)
                for func in (local_mean_direct, local_mean_separable, local_mean_integral):
                    np.testing.assert_allclose(func(img, radius), ref, atol=1e-10)


if __name__ == '__main__':
    unittest.main(verbosity=2)
