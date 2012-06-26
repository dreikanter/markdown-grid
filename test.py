import unittest
from mdx_grid import GridPreprocessor


class GridPreprocessorTest(unittest.TestCase):

    def setUp(self):
        self.pp = GridPreprocessor()
        return

    def test_re_matches(self):
        # matches = GridPreprocessor.re_rowb.matches("-- row 1,2,3 --")
        # pprint(matches)
        self.assertEqual(1, 1)


if __name__ == "__main__":
    unittest.main()
