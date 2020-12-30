import numpy as np
from functools import reduce
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep

BOARD_SIZE = 10  # 5, 10, 15, 20
USER_DATA_DIR = '--user-data-dir=/home/dchen327/.config/google-chrome/Profile 2'
LINK = f'https://www.goobix.com/games/nonograms/?s={BOARD_SIZE}'


class NonogramSolver:
    def __init__(self):
        self.launch_browser()
        self.get_board()

    def launch_browser(self):
        """ Launch chrome and go to game link """
        options = Options()
        if USER_DATA_DIR:
            options.add_argument(USER_DATA_DIR)
        # remove the little popup in corner
        options.add_experimental_option(
            'excludeSwitches', ['enable-automation'])
        # allow instance to keep running after function ends
        options.add_experimental_option('detach', True)
        options.add_argument('--start-maximized')
        self.driver = webdriver.Chrome(options=options)
        self.driver.get(LINK)
        sleep(1)  # wait for page load
        # self.driver.refresh()  # refresh to activate adblocker

    def get_board(self):
        """ Store row/cols of board and rules """
        rules = {'rows': [], 'cols': []}
        rule_elements = self.driver.find_elements_by_class_name(
            'nonogramsDef')  # find rules
        for rule_element in rule_elements:
            print(rule_element.text)

    def solve_line(self, line, rules):
        """ Given a line (row/col) and rules, solve as much as possible """
        K = sum(rules) + len(rules) - 1  # knowledge about current line
        N = len(line)
        # generate possible binary strings
        # ex) rules: [4, 1] -> a4bX1c where a, b, c are strings of Xs
        # ex) a + b + c = N - K, since 4 + 1 + 1 = K
        possible = []  # possible bin strings
        for t in self.partitions(N - K, len(rules) + 1):
            # build binary string
            # don't 1 pad left on first rule
            bin_str = t[0] * '0' + rules[0] * '1'
            for i, rule in enumerate(rules[1:], start=1):
                bin_str += t[i] * '0' + '0' + rule * '1'  # pad left with 0
            bin_str += t[-1] * '0'  # add right side padding
            for i, bit in enumerate(bin_str):
                if (bit == '1' and line[i] == '0') or (bit == '0' and line[i] == '1'):
                    break  # contradiction found
            else:  # no contradictions with line
                possible.append(int(bin_str, 2))
        # if 1, then bitwise AND is only 1 if all are 1
        o_overlap = reduce(lambda x, y: x & y, possible)
        # if 0, then bitwise OR is only 0 if all are 0
        x_overlap = reduce(lambda x, y: x | y, possible)
        o_overlap = bin(o_overlap)[2:].zfill(N)  # convert int to bin string
        x_overlap = bin(x_overlap)[2:].zfill(N)  # convert int to bin string
        for i in range(N):  # set confirmed locations in line
            if o_overlap[i] == '1':
                line[i] = '1'
            if x_overlap[i] == '0':
                line[i] = '0'

        return line

    def partitions(self, n, k):
        """ n is the integer to partition, k is the length of partitions 
            ex) n=5, k=2 -> (5, 0), (4, 1), (3, 2), ..., (0, 5)
        """
        if k == 1:
            if n >= 0:
                yield (n,)
            return
        for i in range(n + 1):
            for result in self.partitions(n-i, k-1):
                yield (i,) + result


if __name__ == "__main__":
    nonogram_solver = NonogramSolver()
    line = np.array(list('||||1||1||'))
    rules = '4'
    rules = list(map(int, rules.split()))
    line = nonogram_solver.solve_line(line, rules)
    print(''.join(line))
