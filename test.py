import unittest
import mdx_grid
import random


class Helpers:
    @staticmethod
    def get_rand(min_val=0, max_val=99):
        return random.randint(min_val, max_val)


class GridPreprocessorTest(unittest.TestCase):

    def setUp(self):
        self.pp = mdx_grid.GridPreprocessor()
        return

    def test_re_matches(self):
        # tag = mdx_grid.GridTagInfo(mdx_grid.GridTags.ROW_OPEN, Helpers.get_rand()).get_tag()
        # matches = mdx_grid.Patterns.rowtag_open.match(tag)
        # self.assertTrue(matches)

        # tag = mdx_grid.GridTagInfo(mdx_grid.GridTags.COL_OPEN, Helpers.get_rand()).get_tag()
        # matches = mdx_grid.Patterns.coltag_open.match(tag)
        # self.assertTrue(matches)

        # tag = mdx_grid.GridTagInfo(mdx_grid.GridTags.COL_CLOSE, Helpers.get_rand()).get_tag()
        # matches = mdx_grid.Patterns.coltag_close.match(tag)
        # self.assertTrue(matches)

        # tag = mdx_grid.GridTagInfo(mdx_grid.GridTags.ROW_CLOSE, Helpers.get_rand()).get_tag()
        # matches = mdx_grid.Patterns.rowtag_close.match(tag)
        # self.assertTrue(matches)
        pass

    def test_cell_params_parsing(self):
        # test_values = [
        #     [[0, 0], ('0,0',)],
        #     [[1, 1], ('1,1',)],
        #     [[123, 456], ('123,456',)],
        #     [[-1, -2], None],
        #     [["potatoes", "potatoes"], None],
        # ]

        # for value, result in test_values:
        #     tag = mdx_grid.GridTagInfo(mdx_grid.GridTags.COL_OPEN, Helpers.get_rand())
        #     tag.span, tag.offset = value
        #     matches = mdx_grid.Patterns.coltag_open.match(tag.get_tag())
        #     actualResult = matches.groups() if matches else None
        #     self.assertTrue(result == actualResult)
        pass


class ParsersTest(unittest.TestCase):

    def setUp(self):
        return

    def test_parse_spanoffset(self):
        test_values = {
            "10": [10, 0],
            "10:20": [10, 20],
            "\t1 : 2\t": [1, 2],
            "": [None, 0],
            ":123": [None, 123],
            "456:": [456, 0],
            "1:abc": [1, 0],
            "abc:1": [None, 1],
        }

        for value in test_values:
            self.assertListEqual(mdx_grid.Parsers.parse_spanoffset(value), test_values[value])

    def test_parse_csints(self):
        test_values = {
            "10": [10],
            "1,2,3": [1, 2, 3],
            "": [],
            "\t  \t": [],
            "  123, 456,\t-789  ": [123, 456, -789],
            "1, 2, potatoes, 3, potatoes": [1, 2, 3],
            "more potatoes": [],
        }

        for value in test_values:
            self.assertListEqual(mdx_grid.Parsers.parse_csints(value), test_values[value])

    def test_parse_row_params(self):
        test_values = {
            "10": [[10], [0]],
            "1,2,3": [[1, 2, 3], [0, 0, 0]],
            "": [[], []],
            "\t  \t": [[], []],
            "  123, 456,\t-789  ": [[123, 456, -789], [0, 0, 0]],
            "1, 2, potatoes, 3, potatoes": [[1, 2, 3], [0, 0, 0]],
            "more potatoes": [[], []],
            "1:4, 2:5, 3:6": [[1, 2, 3], [4, 5, 6]],
            "1:4, 2, 3:6": [[1, 2, 3], [4, 0, 6]],
            " 1 : 4 , 2 : 5, 3\t:\t6": [[1, 2, 3], [4, 5, 6]],
        }

        for value in test_values:
            widths, offsets = mdx_grid.Parsers.parse_row_params(value)
            self.assertListEqual(widths, test_values[value][0])
            self.assertListEqual(offsets, test_values[value][1])


if __name__ == "__main__":
    unittest.main()
