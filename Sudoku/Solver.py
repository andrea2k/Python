import copy
import sys
import math

FILE = 1
ROW = 0
COL = 1
CHOICES = 2
FIRST = 0


# This class is used to read a sudoku file and transform the content of the
# file into a 2d array with corresponding values.
class Sudoku:
    def __init__(self, filename):
        file = open(filename, 'r')
        self.sudoku = []
        for line in file:
            # change the line into int array
            row = list(map(int, line.split()))
            self.sudoku.append(row)
        if not self.sudoku:
            exit("Error reading file")
        self.valid_sudoku()

    # Checks if the sudoku is valid by checking the value and width of the row
    def valid_sudoku(self):
        self.width = len(self.sudoku)
        for row in self.sudoku:
            if len(row) != self.width:
                exit("Row not consistent")
            for value in row:
                if value > self.width:
                    exit("Value too large")


# This class is used to get free values in a cell by giving the corresponding
# row and column,it is also able to return the value of corresponding cell.
class Cell:
    def __init__(self, sudoku, row, col):
        self.sudoku = sudoku
        self.row = row
        self.col = col
        self.width_sudoku = len(self.sudoku)

    def free_in_row(self):
        lst = list(range(1, self.width_sudoku+1))
        row = self.sudoku[self.row]
        return list(set(lst) - set(row))

    def free_in_col(self):
        lst = list(range(1, self.width_sudoku+1))
        col = []
        for row in self.sudoku:
            col.append(row[self.col])
        return list(set(lst) - set(col))

    def free_in_subgrid(self):
        lst = list(range(1, self.width_sudoku+1))
        subgrid = []
        width_subgrid = int(math.sqrt(self.width_sudoku))
        row_block = self.row - self.row % width_subgrid
        col_block = self.col - self.col % width_subgrid
        for row in range(row_block, row_block+width_subgrid):
            for col in range(col_block, col_block+width_subgrid):
                subgrid.append(self.sudoku[row][col])
        return list(set(lst) - set(subgrid))

    def free_in_cell(self):
        return list(set(self.free_in_col()) & set(self.free_in_row()) &
                    set(self.free_in_subgrid()))

    def get_value(self):
        return self.sudoku[self.row][self.col]


# This class is used to check if the given sudoku is full filled and if the
# the sudoku complies with the sudoku rules
class Consistent:
    def __init__(self, sudoku):
        self.sudoku = sudoku
        self.width_sudoku = len(self.sudoku)

    # 'consistent' functions are used to check if there are duplicates in a
    # row,col and subgrid.
    def row_consistent(self, row):
        row = sorted(i for i in self.sudoku[row] if i > 0)
        if len(row) == len(set(row)):
            return True
        else:
            return False

    def col_consistent(self, column):
        col = []
        for row in self.sudoku:
            col.append(row[column])
        col = sorted(i for i in col if i > 0)
        if len(col) == len(set(col)):
            return True
        else:
            return False

    def subgrid_consistent(self, row, column):
        subgrid = []
        width_subgrid = int(math.sqrt(self.width_sudoku))
        row_block = row - row % width_subgrid
        col_block = row - column % width_subgrid
        for row in range(row_block, row_block+width_subgrid):
            for column in range(col_block, col_block+width_subgrid):
                subgrid.append(self.sudoku[row][column])
        subgrid = sorted(i for i in subgrid if i > 0)
        if len(subgrid) == len(set(subgrid)):
            return True
        else:
            return False

    def sudoku_consistent(self):
        range_sudoku = list(range(0, self.width_sudoku))
        for row in range_sudoku:
            for col in range_sudoku:
                if not self.row_consistent(
                        row) or not self.col_consistent(
                            col) or not self.subgrid_consistent(row, col):
                    return False
                else:
                    return True

    # this function is used to check if a sudoku is full filled.
    def sudoku_filled(self):
        for row in self.sudoku:
            row = sorted(i for i in row if i > 0)
            if len(row) < self.width_sudoku:
                return False
        return True


# This class is used to get the constraints of a sudoku.
class Constraints:
    def __init__(self, sudoku):
        self.sudoku = sudoku
        self.width_sudoku = len(self.sudoku)

    # For each empty cell, append the tupple(row,col,choices) into the list.
    def get_constraints(self):
        range_sudoku = list(range(0, self.width_sudoku))
        constraints = []
        for row in range_sudoku:
            for col in range_sudoku:
                cell = Cell(self.sudoku, row, col)
                if cell.get_value() == 0:
                    constraints.append((row, col, cell.free_in_cell()))
        constraints = sorted(constraints, key=lambda a: len(a[2]))
        return constraints


# This class is used to solve a sudoku by a breadth search algorithme.
# All the solutions will be appended in a list.
class Solver:
    def __init__(self, sudoku):
        self.sudoku = sudoku
        self.solution = []
        self.queue = []
        check = Consistent(sudoku)
        if not check.sudoku_consistent():
            exit("No solution for this sudoku")
        self.append_queue(self.sudoku)
        self.solver()
        self.print_solver()

    # append into queue
    def append_queue(self, sudoku):
        self.queue.append(sudoku)

    # pop the queue
    def pop_queue(self):
        return self.queue.pop(0)

    # for a empty cell, make deepcopy of the sudoku and fill all the possible
    # choices and append into queue.
    def fill_sudoku(self, sudoku, constraint):
        choices = constraint[CHOICES]
        row = constraint[ROW]
        col = constraint[COL]
        for choice in choices:
            sud = copy.deepcopy(sudoku)
            sud[row][col] = choice
            self.append_queue(sud)

    # Append consistent/full filled sudoku into solution list, for not full
    # filled sudoku try all the possible choices.
    def solver(self):
        while self.queue:
            sudoku = self.pop_queue()
            check = Consistent(sudoku)
            if check.sudoku_consistent() and check.sudoku_filled():
                self.solution.append(sudoku)
            if check.sudoku_consistent():
                constraints = Constraints(sudoku).get_constraints()
                if constraints:
                    self.fill_sudoku(sudoku, constraints[FIRST])

    # Print all the solutions.
    def print_solver(self):
        number_of_solution = len(self.solution)
        if self.solution:
            for i in range(0, number_of_solution):
                self.print_sudoku(self.solution[i])
            print("\n")
    # Print sudoku

    def print_sudoku(self, sudoku):
        for i in sudoku:
            print(*i)


def main():
    filename = sys.argv[FILE]
    sudoku = Sudoku(filename)
    Solver(sudoku.sudoku)


main()
