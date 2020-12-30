import numpy as np
from functools import reduce


class NonogramSolver:
    def solve_line(self, line, rules):
        """ Given a line (row/col) and rules, solve as much as possible """
        K = sum(rules) + len(rules) - 1  # knowledge about current line
        N = len(line)
        if 2 * K > N:  # there are overlaps, so we can solve
            # generate possible binary strings
            # ex) rules: [4, 1] -> a4bX1c where a, b, c are strings of Xs
            # ex) a + b + c = N - K, since 4 + 1 + 1 = K
            possible = []  # possible bin strings
            for t in self.partitions(N - K, len(rules) + 1):
                # build binary string
                bin_str = t[0] * '0' + rules[0] * '1'
                for i, rule in enumerate(rules[1:], start=1):
                    bin_str += t[i] * '0' + '0' + rule * '1'  # pad left with 0
                bin_str += t[-1] * '0'  # add right side padding
                for i in range(N):
                    if (bin_str[i] == '1' and line[i] == '0') or (bin_str[i] == '0' and line[i] == '1'):
                        break  # contradiction found
                else:
                    possible.append(int(bin_str, 2))
            # if 1, then bitwise AND is only 1 if all are 1
            o_overlap = reduce(lambda x, y: x & y, possible)
            # if 0, then bitwise OR is only 0 if all are 0
            x_overlap = reduce(lambda x, y: x | y, possible)
            o_overlap = bin(o_overlap)[2:].zfill(N)
            x_overlap = bin(x_overlap)[2:].zfill(N)
            print('1s confirmed', o_overlap)
            print('0s confirmed', x_overlap)

    def partitions(self, n, k):
        """ n is the integer to partition, k is the length of partitions """
        if k < 1:
            return
        if k == 1:
            if n >= 0:
                yield (n,)
            return
        for i in range(n + 1):
            for result in self.partitions(n-i, k-1):
                yield (i,) + result


if __name__ == "__main__":
    nonogram_solver = NonogramSolver()
    line = np.array(['1', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '])
    rules = '5 2'
    rules = list(map(int, rules.split()))
    print(nonogram_solver.solve_line(line, rules))
