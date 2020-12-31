import numpy as np
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from functools import reduce
from time import sleep

BOARD_SIZE = 25  # 5, 10, 15, 20
USER_DATA_DIR = '--user-data-dir=/home/dchen327/.config/google-chrome/Profile 2'


class NonogramSolver:
    def __init__(self, board_size):
        self.board_size = board_size
        self.board = np.full((board_size, board_size), fill_value='|')
        self.cells = []
        self.rules = []
        self.stack = []  # for storing stack of rules to be processed

    def setup_game(self):
        """ Launch browser and get board """
        link = f'https://www.goobix.com/games/nonograms/?s={self.board_size}'
        self.launch_browser(link)
        self.get_rules()
        self.get_cell_elements()
        self.solve_game()

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
        init_knowledge = []
        # store rules
        for i, rule_element in enumerate(rule_elements[:2 * self.board_size]):
            rule = list(map(int, rule_element.text.split()))
            self.rules.append(rule)
            init_knowledge.append((i, self.get_knowledge(rule)))
        # initial stack sorted by knowledge
        self.stack = [i for i, knowledge in sorted(
            init_knowledge, key=lambda x: x[1])]

    def get_cell_elements(self):
        """ Store all cell elements for clicking """
        self.cells = self.driver.find_elements_by_class_name('nonoCell')

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
            for i, num in enumerate(rule[1:], start=1):
                bin_str += t[i] * '0' + '0' + num * '1'  # pad left with 0
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
        init_stack = self.stack[:]
        num_without_change = 0
        while self.stack:
            idx = self.stack.pop()
            board_idx = self.get_board_idx(idx)
            line = self.board[board_idx].copy()
            if self.stack == []:  # reset stack
                self.stack = init_stack[:]
            if '|' not in line:
                continue
            line = self.solve_line(line, self.rules[idx])
            # changes made
            if not np.array_equal(line, self.board[board_idx]):
                try:
                    self.click_squares(idx, line)
                except selenium.common.exceptions.StaleElementReferenceException:
                    break  # board solved
                num_without_change = 0
            else:
                num_without_change += 1

            if '|' not in self.board:  # complete
                break

            # guess (indeterminate)
            # if num_without_change > 3 * self.board_size:
            #     print('guess')
            #     num_without_change = 0
            #     # set a blank to 1
            #     for i in range(self.board_size):
            #         changed = False
            #         for j in range(self.board_size):
            #             if self.board[i, j] == '|':
            #                 self.board[i, j] = '1'
            #                 changed = True
            #                 break
            #         if changed:
            #             break

    def click_squares(self, idx, line):
        """ Fill in squares given an idx and a solved line, update in self.board """
        board_idx = self.get_board_idx(idx)
        curr_line = self.board[board_idx]
        for i, val in enumerate(line):
            if val != '|' and curr_line[i] == '|':  # update in board
                self.board[board_idx][i] = val
                if idx < self.board_size:  # col
                    row, col = i, idx
                    next_idx = i  # idx to add to stack
                else:  # row
                    row, col = idx - self.board_size, i
                    next_idx = i + self.board_size

                self.stack.append(next_idx)
                cell = self.cells[row * self.board_size + col]
                cell.click()
                if val == '0':  # double click for X
                    cell.click()

    def get_board_idx(self, idx):
        """ Given idx from 0 to 2 * board_size - 1, return np index """
        if idx < self.board_size:  # column
            board_idx = (slice(None), idx)  # [:, idx], select col
        else:  # row
            board_idx = (idx - self.board_size, slice(None))
        return board_idx

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
