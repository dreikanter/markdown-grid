import unittest
import mdx_grid
import random
import markdown
from pprint import pprint


class Helpers:
    @staticmethod
    def get_rand(min_val=0, max_val=99):
        return random.randint(min_val, max_val)


# class GridPreprocessorTest(unittest.TestCase):

#     def setUp(self):
#         self.pp = mdx_grid.GridPreprocessor()
#         return

#     def test_cmd_matches(self):
#         cmd = mdx_grid.Command(mdx_grid.ROW_OPEN_CMD)
#         matches = mdx_grid.Patterns.row_open_cmd.match(str(cmd))
#         self.assertTrue(matches)

#         cmd = mdx_grid.Command(mdx_grid.COL_OPEN_CMD)
#         cmd.style = Helpers.get_rand()
#         matches = mdx_grid.Patterns.col_open_cmd.match(str(cmd))
#         self.assertTrue(matches)

#         cmd = str(mdx_grid.Command(mdx_grid.COL_CLOSE_CMD))
#         matches = mdx_grid.Patterns.col_close_cmd.match(str(cmd))
#         self.assertTrue(matches)

#         cmd = str(mdx_grid.Command(mdx_grid.ROW_CLOSE_CMD))
#         matches = mdx_grid.Patterns.row_close_cmd.match(str(cmd))
#         self.assertTrue(matches)


# class ParsersTest(unittest.TestCase):

#     def setUp(self):
#         return

#     def test_expand_shortcuts(self):
#         test_values = [
#             ["4:1", "span4 offset1", True],
#             ["4:1", "4:1", False],
#             ["6", "span6", True],
#             ["8", "8", False],
#             ["potatoes", "potatoes", True],
#             ["potatoes1", "potatoes1", True],
#             ["potatoes1:1", "potatoes1:1", True],
#             ["potatoes:1", "potatoes:1", True],
#         ]

#         for value, result, is_bootstrap in test_values:
#             actual_result = mdx_grid.Parsers.expand_shortcuts(value, is_bootstrap)
#             self.assertEqual(result, actual_result)

#     def test_col_args_parsing(self):
#         test_values = [
#             ["span4 offset1, span4, span2", None, ['span4 offset1', 'span4', 'span2']],
#             ["4:1, 4, 3", 'bootstrap', ['span4 offset1', 'span4', 'span3']],
#             ["1,2,3:6", 'bootstrap', ['span1', 'span2', 'span3 offset6']],
#             ["1,,1", 'bootstrap', ['span1', '', 'span1']],
#             ["1,2,3", 'skeleton', ['1', '2', '3']],
#             ["1,,1", 'skeleton', ['1', '', '1']],
#             [",", None, ['', '']],
#             ["", None, []],
#         ]

#         for args, profile, result in test_values:
#             cmd = mdx_grid.Command(mdx_grid.ROW_OPEN_CMD)
#             cmd.style = args

#             marker = "--%s %s--" % (str(cmd), args)
#             matches = mdx_grid.Patterns.row_open.match(marker)
#             self.assertTrue(matches and matches.groups())

#             actual_result = mdx_grid.Parsers.parse_row_args(matches.group(1), profile)
#             self.assertListEqual(result, actual_result)


# class GridTagExapnsionTest(unittest.TestCase):

#     def setUp(self):
#         self.conf = mdx_grid.GridConf.get_profile(mdx_grid.DEFAULT_PROFILE)

#     def conf_param_getter(self, param):
#         if param in self.config:
#             return self.config[param]
#         else:
#             return None

#     def test_get_html(self):
#         return


class AliasProcessingTest(unittest.TestCase):
    def setUp(self):
        self.conf = mdx_grid.process_configuration(None)

    def test_expand_aliases(self):
        test_values = [
            ('1', 'span1'),
            ('1 2', 'span1 span2'),
            ('1:2 3', 'span1 offset2 span3'),
            ('1:2 3:4', 'span1 offset2 span3 offset4'),
            ('potatoes potatoes', 'potatoes potatoes'),
            ('potatoes 1 2:3', 'potatoes span1 span2 offset3'),
            ('potatoes1 potatoes1:2 2:3potatoes',
             'potatoes1 potatoes1:span2 span2:3potatoes'),
        ]

        self.assertTrue(self.conf['aliases'])

        for value, result in test_values:
            actual_result = mdx_grid.expand_aliases(value, self.conf['aliases'])
            self.assertEqual(result, actual_result)

    def test_parse_row_args(self):
        test_values = [
            ('1, 2', ['span1', 'span2']),
            ('1 2, 3:4', ['span1 span2', 'span3 offset4']),
            ('1:2, potatoes', ['span1 offset2', 'potatoes']),
            ('', []),
            (None, []),
        ]

        self.assertTrue(self.conf['aliases'])

        for value, result in test_values:
            actual_result = mdx_grid.parse_row_args(value, self.conf['aliases'])
            self.assertListEqual(result, actual_result)


# class PostprocessorTest(unittest.TestCase):
#     def setUp(self):
#         return

#     def test_expand_cmd(self):
#         test_values = [
#             ('row;col(span4)', ''),
#             ('endcol;col(span2 offset1)', ''),
#             ('endcol;endrow', ''),
#             ('', ''),
#         ]

#         md = markdown.Markdown()
#         pp = mdx_grid.GridPostprocessor(md)

#         for value, result in test_values:
#             pp.expand_cmd(value)


class MarkdownTest(unittest.TestCase):
    def setUp(self):
        self.md = markdown.Markdown(extensions=['grid'])

    def test_convertion(self):
        self.assertEqual(self.md.convert(''), '')


if __name__ == "__main__":
    unittest.main()
