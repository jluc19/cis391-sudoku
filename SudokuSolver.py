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

	
	def forward_check(self, var, value, assignment):
			success = True
			#printGrid(self)
			#print "Var, value: ", var, value
			print "Assignment: ", assignment, "\n"
			remaining = dict((k,v) for k,v in self.domain.iteritems() if len(v) > 1) 
			#print "REMAINING: ", remaining
			#print "57 check: ", self.arcs[54]
			print "DOMAIN: ", self.domain
			#print "PRUNED: ", self.pruned, "\n", self.arcs[var]
			#pruning
			for arc in self.arcs[var]:
				if arc not in assignment:
					print "INFO Arc, remove, value: ", arc, self.domain[arc], value
					for to_remove in self.domain[arc]:
						print "TO-REMOVE, ", to_remove, int(value[0])
						if not self.constraint(int(value[0]), to_remove):
							self.pruned[var].append((arc, to_remove))
							self.domain[arc].remove(to_remove)
							if len(self.domain[arc]) == 1:
								print "PRINT ARC :", arc, self.domain[arc]
								success = self.forward_check(arc, self.domain[arc], assignment)
								print "Back Out!: ", var, value
			print "SUCCESS?: ", success
			if success:
				print "HERE I AM:", arc
				assignment[var] = value
				self.domain[var] = value
			else:
				if(value in self.domain[var]):
					for (oldVar, oldValue) in self.pruned[var]:
						self.domain[oldVar].append(oldValue)
						self.pruned[var] = []
					self.domain[var].remove(value)
				return False
							#elif len(self.domain[arc]) < 1:	
							#	return False
			return True

	def add_assign(self, var, val, assignment=None):
			#print "VAL VAR: ", val, var
			old_domain = copy.deepcopy(self.domain)
			#print "old_domain: ", self.domain
			success = self.forward_check(var, val, assignment)
			return success

	def remove_assign(self, var, assignment):
		if var in assignment:
			#self.domain[var] = self.domains[var][:]
			del assignment[var]


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

def solve_p6(sudokuGrid):
	#we run the same algorithm as problem 4, with a twist of guessing
	#once traditional methods fail we run backtracking to recursively guess
	solve_p4(sudokuGrid)
	output = None
	if(not sudokuGrid.solved()):
		assignment = dict((k,v) for k,v in sudokuGrid.domain.iteritems() if len(v) == 1) 
		sudokuGrid.pruned = dict((v, []) for v in sudokuGrid.var)
		output = backtrack(sudokuGrid, assignment)
		if output is None:
			print "Backtracking didn't work. \n"
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

#adapted from slides/AI Textbook
def backtrack(sudokuGrid, assignment):
	if len(assignment) == len(sudokuGrid.var):
		return assignment
	var = assign_var(sudokuGrid, assignment)
	print "VAR SELECTED: ", var, sudokuGrid.domain[var]
	for value in sudokuGrid.domain[var][::-1]:
		success = sudokuGrid.add_assign(var, value, assignment)
		if success:
			result = backtrack(sudokuGrid, assignment)
			if result is not None:
				return result
		else:
			sudokuGrid.remove_assign(var, assignment)
	return None

#we use Most Constrained Variable (MRV) to determine the unassigned value
def assign_var(sudokuGrid, assignment):
	unassigned = [v for v in sudokuGrid.var if v not in assignment]
	#print "assigned: ", assignment
	min_val = 0
	ret_var = 0
	for var in unassigned:
		if -len(sudokuGrid.domain[var]) < min_val:
			ret_var = var
	return ret_var
	#return argmax(unassigned, lambda var: -len(sudokuGrid.domain[var]))


if __name__ == '__main__':
	grid = read(sys.argv[1])
	runSudoku= SudokuGrid(grid)
	if(sys.argv[2] == '1'):
		solve_p2(runSudoku)
	elif(sys.argv[2] == '2'):
		solve_p4(runSudoku)
	else:
		solve_p6(runSudoku)
	printGrid(runSudoku)


