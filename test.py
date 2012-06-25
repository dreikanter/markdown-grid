from pprint import pprint
import markdown
from mdx_grid import GridPreprocessor


def test_pre_match():
    matches = None
    if GridPreprocessor.matches(GridPreprocessor.re_rowb, "-- row 1,2,3 --", matches):
        pprint(matches)


if __name__ == "__main__":
    test_pre_match()
