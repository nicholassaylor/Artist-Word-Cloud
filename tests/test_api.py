import unittest
from musicworldcloud.musicwordcloud import find_api, build_artist_page


class TestApi(unittest.TestCase):
    def test_api_returns(self):
        """Test various artists with simple names"""
        for name in ["Seether", "Taylor Swift", "Sza", "Metallica", "Charli XCX", "TOMORROW X TOGETHER"]:
            with self.subTest(name=name):
                self.assertNotEqual(find_api(build_artist_page(name), name), "", f"{name} failed.")

    def test_api_robust(self):
        """Tests various artists with complex names"""
        for name in ["AC/DC", "J. Cole", "Beyoncé", "Björk", "D'Angelo"]:
            with self.subTest(name=name):
                self.assertNotEqual(find_api(build_artist_page(name), name), "", f"{name} failed.")

    def test_not_implemented(self):
        """Test artists with names in scripts not supported"""
        # These artists are likely to have romanized spellings that are supported
        # Romanized Names are Camellia, Jay Chou, Epik High,
        for name in ["かめりあ", "周杰倫", "에픽하이"]:
            with self.subTest(name=name):
                self.assertEqual(find_api(build_artist_page(name), name), "", f"{name} failed.")

    def test_api_fails(self):
        """Tests names where the API call should fail"""
        for name in ["", "/", "asddasnopdas", ";"]:
            with self.subTest(name=name):
                self.assertEqual(find_api(build_artist_page(name), name), "", f"{name} failed.")

    def test_api_edge_cases(self):
        """Following tests should pass despite looking like it should fail"""
        # These succeed due to unidecode being run on the strings
        for name in [";return", ";return;", "return;", "?return"]:
            with self.subTest(name=name):
                self.assertNotEqual(find_api(build_artist_page(name), name), "", f"{name} failed.")


if __name__ == '__main__':
    unittest.main()
