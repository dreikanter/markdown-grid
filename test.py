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

    def test_cmd_matches(self):
        cmd = mdx_grid.GridCmdInfo(mdx_grid.GridCmd.ROW_OPEN)
        matches = mdx_grid.Patterns.row_open_cmd.match(str(cmd))
        self.assertTrue(matches)

        cmd = mdx_grid.GridCmdInfo(mdx_grid.GridCmd.COL_OPEN)
        cmd.style = Helpers.get_rand()
        matches = mdx_grid.Patterns.col_open_cmd.match(str(cmd))
        self.assertTrue(matches)

        cmd = str(mdx_grid.GridCmdInfo(mdx_grid.GridCmd.COL_CLOSE))
        matches = mdx_grid.Patterns.col_close_cmd.match(str(cmd))
        self.assertTrue(matches)

        cmd = str(mdx_grid.GridCmdInfo(mdx_grid.GridCmd.ROW_CLOSE))
        matches = mdx_grid.Patterns.row_close_cmd.match(str(cmd))
        self.assertTrue(matches)


class ParsersTest(unittest.TestCase):

    def setUp(self):
        return

    def test_expand_shortcuts(self):
        test_values = [
            ["4:1", "span4 offset1", True],
            ["4:1", "4:1", False],
            ["6", "span6", True],
            ["8", "8", False],
            ["potatoes", "potatoes", True],
            ["potatoes1", "potatoes1", True],
            ["potatoes1:1", "potatoes1:1", True],
            ["potatoes:1", "potatoes:1", True],
        ]

        for value, result, is_bootstrap in test_values:
            actual_result = mdx_grid.Parsers.expand_shortcuts(value, is_bootstrap)
            self.assertEqual(result, actual_result)

    def test_col_args_parsing(self):
        test_values = [
            ["span4 offset1, span4, span2", None, ['span4 offset1', 'span4', 'span2']],
            ["4:1, 4, 3", 'bootstrap', ['span4 offset1', 'span4', 'span3']],
            ["1,2,3:6", 'bootstrap', ['span1', 'span2', 'span3 offset6']],
            ["1,,1", 'bootstrap', ['span1', '', 'span1']],
            ["1,2,3", 'skeleton', ['1', '2', '3']],
            ["1,,1", 'skeleton', ['1', '', '1']],
            [",", None, ['', '']],
            ["", None, []],
        ]

        for args, profile, result in test_values:
            cmd = mdx_grid.GridCmdInfo(mdx_grid.GridCmd.ROW_OPEN)
            cmd.style = args

            marker = "--%s %s--" % (str(cmd), args)
            matches = mdx_grid.Patterns.row_open.match(marker)
            self.assertTrue(matches and matches.groups())

            actual_result = mdx_grid.Parsers.parse_row_args(matches.group(1), profile)
            self.assertListEqual(result, actual_result)


if __name__ == "__main__":
    unittest.main()
