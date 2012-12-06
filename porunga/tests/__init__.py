import os
from porunga.utils.compat import unittest


def collector():
    start_dir = os.path.abspath(os.path.dirname(__file__))
    return unittest.defaultTestLoader.discover(start_dir)

def main():
    unittest.main()

if __name__ == '__main__':
    main()

