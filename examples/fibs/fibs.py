import fileinput
import re
import sys


def fibs(n, m):
    """
    Yields Fibonacci numbers starting from ``n`` and ending at ``m``.
    """
    a = b = 1
    for x in range(3, m + 1):
        a, b = b, a + b
        if x >= n:
            yield b

def main():
    fin = fileinput.input()
    n, m = map(int, re.findall(r'\d+', fin.readline()))
    result = ' '.join([str(f) for f in fibs(n, m)])
    sys.stdout.write(result)


if __name__ == '__main__':
    main()

