import sys, itertools, copy
from datetime import datetime

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
		self.pruning = dict((var, []) for var in self.var)
		self.original_domain = self.domain

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

	def solved(self):
		return len(list(itertools.chain(*self.domain.values()))) == len(self.var)

	def undo_forward(self, var):
		for (oldVar, oldValue) in self.pruning[var]:
			if oldValue not in self.domain[oldVar]:
				self.domain[oldVar].append(oldValue)
			self.pruning[var] = []

	def forward_check(self, var, assignment):
		for arc in self.arcs[var]:
			for value in self.domain[arc]:
				if assignment[var] == value:
					self.pruning[var].append((arc, value))
					self.domain[arc].remove(value)
				if self.domain[arc] == []:
					self.undo_forward(var)
					return False	
		return True

#_____________________________________________________________________________
#solver without guessing
def SudokuMediumSolver(sudokuGrid):
	while not sudokuGrid.solved():
		old_domain = copy.deepcopy(sudokuGrid.domain)
		runAC3(sudokuGrid)
		assign_stragglers(sudokuGrid)
		new_domain = sudokuGrid.domain
		updateRCB(sudokuGrid)
		if new_domain != old_domain:
			continue
		else:
			break

def SudokuSolver(sudokuGrid):
	#once traditional methods fail we run backtracking to recursively guess
	SudokuMediumSolver(sudokuGrid)
	output = None
	sudokuGrid.original_domain = copy.deepcopy(sudokuGrid.domain)
	if(not sudokuGrid.solved()):
		assignment = dict((key,value) for key,value in sudokuGrid.domain.iteritems() if len(value) == 1) 
		output = backtrack(sudokuGrid, assignment)
		if output is None:
			print "Uh oh. There was a problem. \n"
		else:
			updateRCB(sudokuGrid)

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
		for number in group_dict:
			if len(group_dict[number]) == 1:
				sudokuGrid.domain[group_dict[number][0]] = [str(number)]

def printGrid(sudokuGrid):
	if(sudokuGrid.solved()):
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
		if all(x == y for y in sudokuGrid.domain[b]):
			sudokuGrid.domain[a].remove(x)
			revised = True
	return revised

#warped version based on AI Slides & Textbook
def backtrack(sudokuGrid, assignment):
	if sudokuGrid.solved():
		return True
	while not sudokuGrid.solved():
		if len(assignment) == len(sudokuGrid.var):
			break
		var = assign_var(sudokuGrid, assignment)
		var_domain = sudokuGrid.domain[var]
		assignment[var] = var_domain[0]
		sudokuGrid.domain[var] = [var_domain[0]]
		successful_guess = sudokuGrid.forward_check(var, assignment)
		if successful_guess:
			if not backtrack(sudokuGrid, assignment):
				sudokuGrid.undo_forward(var)
				sudokuGrid.domain[var] = var_domain
				assignment.pop(var,0)
				if len(sudokuGrid.domain[var]) == 1:
					sudokuGrid.pruning[var] = []
					sudokuGrid.domain[var] = sudokuGrid.original_domain[var]
					return False
				else:
					sudokuGrid.domain[var] = var_domain[1:]
			else:
				return True
		else:
			assignment.pop(var,0)
			sudokuGrid.domain[var] = var_domain[1:]
			if sudokuGrid.domain[var] == []:
				sudokuGrid.domain[var] = sudokuGrid.original_domain[var]
				return False
			else:
				continue
	assign_stragglers(sudokuGrid)
	updateRCB(sudokuGrid)

#we use Most Constrained Variable (MRV) to determine the unassigned value
def assign_var(sudokuGrid, assignment):
	unassigned = [v for v in sudokuGrid.var if v not in assignment]
	min_val = 9
	result = 0
	for option in unassigned:
		if len(sudokuGrid.domain[option]) < min_val:
			min_val = len(sudokuGrid.domain[option])
			result = option
	return result

if __name__ == '__main__':
	startTime = datetime.now()
	grid = read(sys.argv[1])
	runSudoku= SudokuGrid(grid)
	SudokuSolver(runSudoku)
	printGrid(runSudoku)
	print("Time to solve: ", str(datetime.now() - startTime))