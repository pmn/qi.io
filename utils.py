from datetime import datetime
from decimal import Decimal
import unittest


def nextid( start_id=None):
    """Generate a valid new id."""
    test_id = datetime.now().strftime("%Y%m%d")
    if start_id == None:
        return datetime.now().strftime(test_id + ".01")
    else:
        if start_id.startswith(test_id):
            return str(round(float(start_id) + .01, 2))
        else:
            return test_id + ".01"


class TextNextid(unittest.TestCase):
    def test_basic(self):
        test_id = datetime.now().strftime("%Y%m%d.01")
        test_id_2 = datetime.now().strftime("%Y%m%d.02")
        test_cases = (
            (None, test_id),
            (test_id, test_id_2),
            ('20111101.01', test_id),
            )
        for testdate, result in test_cases:
            print "comparing {} and {}".format(nextid(testdate), result)
            self.assertTrue(str(nextid(testdate)) == result)


if __name__ == "__main__":
    unittest.main()
