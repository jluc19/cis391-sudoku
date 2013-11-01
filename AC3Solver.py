import re, sys, itertools, copy
from utils import argmax

def read(filename):
	inFile=open(filename, "r")
	data = inFile.readlines()
	grid=[]
	for line in data:
		row = []
		for letter in line:
			if(letter != "\n"):
				row.extend(letter)
		grid.append(row)
	inFile.close()
	return grid

class SudokuGrid(object):
	startingDomain = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
	
	def __init__(self, grid):
		self.grid = grid
		self.domain = dict((var, self.startingDomain[:] if value == '*' else [value]) for var, value in enumerate(list(itertools.chain(*grid))))
		self.var = self.domain.keys()
		self.arcs = self.makeArcs(grid)

		self.rows = grid
		self.cols = [[grid[x][y] for x in range(9)] for y in range(9)]
		box_cells = [(x % 3, x / 3) for x in range(0, 9)]
		self.boxes = [[grid[x*3+a][y*3+b] for a, b in box_cells] for x, y in box_cells]
		
	def makeArcs(self, grid):
		#creates the rows, columns, and box options from the grid
		cols = [[9*x+y for x in range(9)] for y in range(9)]
		rows = [[9*y+x for x in range(9)] for y in range(9)]
		box_cells = [(x % 3, x / 3) for x in range(0, 9)]
		boxes = [[rows[x*3+a][y*3+b] for a, b in box_cells] for x, y in box_cells]
		rcb = (rows + cols + boxes)
		self.rcb = rcb

		overlap = dict((i, [group for group in rcb if i in group])  for i in self.var)
		arcSet = dict((i, set(list(itertools.chain(*overlap[i])))-set([i])) for i in self.var)
		return arcSet

	def constraint(self, x, y):
		return x != y

	def solved(self):
		return len(list(itertools.chain(*self.domain.values()))) == len(self.var)

#_____________________________________________________________________________
#Solving functions (problems 2,4,6)

def solve_p2(sudokuGrid):
	runAC3(sudokuGrid)
	updateRCB(sudokuGrid)

def solve_p4(sudokuGrid):
	while not sudokuGrid.solved():
		old_domain = copy.deepcopy(sudokuGrid.domain)
		runAC3(sudokuGrid)
		updateRCB(sudokuGrid)
		assign_stragglers(sudokuGrid)
		new_domain = sudokuGrid.domain
		if new_domain != old_domain:
			continue
		else:
			break

#_____________________________________________________________________________
#Utility Functions

def updateRCB(sudokuGrid):
	domain = sudokuGrid.domain
	sudokuGrid.grid = [list(itertools.chain(*[domain[9*j+i] if len(domain[9*j+i]) == 1 else '*' for i in range(0,9)])) for j in range(0,9)]
	grid = sudokuGrid.grid
	sudokuGrid.rows = grid
	sudokuGrid.cols = [[grid[x][y] for x in range(9)] for y in range(9)]
	box_cells = [(x % 3, x / 3) for x in range(0, 9)]
	sudokuGrid.boxes = [[grid[x*3+a][y*3+b] for a, b in box_cells] for x, y in box_cells]

def assign_stragglers(sudokuGrid):
	for group in sudokuGrid.rcb:
		group_dict = dict((i, [index for index in group if str(i) in sudokuGrid.domain[index]]) for i in range(1, 10))
		#print "GROUP DICT: ", group_dict
		for number in group_dict:
			if len(group_dict[number]) == 1:
				sudokuGrid.domain[group_dict[number][0]] = [str(number)]

def printGrid(sudokuGrid):
	if(1):
	#if(sudokuGrid.solved()):
		endGrid = sudokuGrid.grid
		print "Completed Sudoku:"
		for row in endGrid:
			for i in row:
				print(i),
			print "\n"
	else:
		print "No Solution, Remaining Domains: "
		for domain in sudokuGrid.domain:
			if len(sudokuGrid.domain[domain]) > 1:
				print "Index: ", domain, "Domain: ", sudokuGrid.domain[domain]
#_____________________________________________________________________________
#Functional Algorithms

#adapted from code in AI Textbook
def runAC3(sudokuGrid):
	queue = [(i, k) for i in sudokuGrid.var for k in sudokuGrid.arcs[i]]
	while queue:
		(i, j) = queue.pop()
		if revise(sudokuGrid, i, j):
			for k in sudokuGrid.arcs[i]:
				queue.append((k, i))

#adapted from code in AI Textbook
def revise(sudokuGrid, a, b):
	revised = False
	for x in sudokuGrid.domain[a]:
		if all(not sudokuGrid.constraint(x,y) for y in sudokuGrid.domain[b]):
			sudokuGrid.domain[a].remove(x)
			revised = True
	return revised

#to run the function as the AC3 solver, type 'python AC3Solver.py "puzzle" 1'
if __name__ == '__main__':
	grid = read(sys.argv[1])
	runSudoku= SudokuGrid(grid)
	if(sys.argv[2] == '1'):
		solve_p2(runSudoku)
	elif(sys.argv[2] == '2'):
		solve_p4(runSudoku)
	printGrid(runSudoku)


