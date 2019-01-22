import numpy as np
import math

def main():
    mark = np.ones(10000000)

    for i in range(2, int(math.sqrt(len(mark)))):
        for j in range(i*i, len(mark), i):
            mark[j] = 0

    for i in range(len(mark)):
        if mark[i]:
            print(f"{i}")


if __name__ == '__main__':
    main()
