import numpy as np


class NonogramSolver:
    def solve_line(self, line, rules):
        """ Given a line (row/col) and rules, solve as much as possible """
        return 5

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
    line = np.array(['', '', '', '', ''])
    rule = [5]
    print(nonogram_solver.solve_line(line, rule))
    print(list(nonogram_solver.partitions(5, 2)))
