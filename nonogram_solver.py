import numpy as np
from functools import reduce
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep

BOARD_SIZE = 10  # 5, 10, 15, 20
USER_DATA_DIR = '--user-data-dir=/home/dchen327/.config/google-chrome/Profile 2'


class NonogramSolver:
    def __init__(self, board_size):
        self.board_size = board_size
        self.board = np.full((board_size, board_size), fill_value='|')
        self.rules = []

    def setup_game(self):
        """ Launch browser and get board """
        link = f'https://www.goobix.com/games/nonograms/?s={self.board_size}'
        self.launch_browser(link)
        self.get_rules()

    def launch_browser(self, link):
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
        self.driver.get(link)
        sleep(1)  # wait for page load
        # self.driver.refresh()  # refresh to activate adblocker

    def get_rules(self):
        """
        Store row/cols of board and rules in self.rules 
        rule format: ([rules], row/col idx, knowledge)
        ex) ([2, 4], 3, 7)
        cols are 0 to board_size-1, rows are board_size to 2 * board_size - 1
        knowledge is sum(rules) + len(rules) - 1
        """
        rule_elements = self.driver.find_elements_by_class_name(
            'nonogramsDef')  # find rules
        # store rules
        for i, rule_element in enumerate(rule_elements[:2 * self.board_size]):
            rule = list(map(int, rule_element.text.split()))
            self.rules.append((rule, i, self.get_knowledge(rule)))

        self.rules.sort(key=lambda x: x[2])

    def solve_line(self, line, rule):
        """ Given a line (row/col) and rule, solve as much as possible """
        if rule == []:  # no rules, all must be X
            line.fill('0')
            return line
        K = self.get_knowledge(rule)  # knowledge about current line
        N = len(line)
        # generate possible binary strings
        # ex) rules: [4, 1] -> a4bX1c where a, b, c are strings of Xs
        # ex) a + b + c = N - K, since 4 + 1 + 1 = K
        possible = []  # possible bin strings
        for t in self.partitions(N - K, len(rule) + 1):
            # build binary string
            # don't 1 pad left on first rule
            bin_str = t[0] * '0' + rule[0] * '1'
            for i, rule in enumerate(rule[1:], start=1):
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

    def solve_game(self):
        stack = []
        while stack:
            stack.append(rules.pop())

    def get_knowledge(self, rule):
        """ Returns a measure of how much we know given the current rule """
        return sum(rule) + len(rule) - 1

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
    nonogram_solver = NonogramSolver(BOARD_SIZE)
    nonogram_solver.setup_game()
    # line = np.array(list('|||||'))
    # rules = '3'
    # rules = list(map(int, rules.split()))
    # line = nonogram_solver.solve_line(line, rules)
    # print(''.join(line))
