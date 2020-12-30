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
                    print(i, rule)
                    bin_str += t[i] * '0' + rule * '1'
                bin_str += t[-1] * '0'  # add right side padding
                possible.append(int(bin_str, 2))
            overlap = reduce(lambda x, y: x & y, possible)
            print(bin(overlap)[2:].zfill(N))

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
    line = np.array(['', '', '', '', '', '', '', '', '', ''])
    rule = [8]
    print(nonogram_solver.solve_line(line, rule))
