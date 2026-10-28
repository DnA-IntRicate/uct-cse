# Simple program to accept a series of Python statements as input and evaluate them.
import sys


def main():
    exec(sys.stdin.readline())
    for line in sys.stdin:
        print(eval(line))

if __name__=='__main__':
    main()
