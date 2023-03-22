from random import randint
from select import select
import multiprocessing as mp
from multiprocessing import Manager
import numpy as np

def getBoard(queensArray):
    #Converts queen array into 2d board array
    board = np.zeros(shape=(len(queensArray),len(queensArray)))
    for i in range(len(queensArray)):
        board[queensArray[i], i] = 1
    return board

def initializePopulation(populationCount, queenCount):
    rng = np.random.default_rng()
    initialPopulationArray = []
    #create random population of queens of specified count 
    for i in range(populationCount):
        queensArray = rng.integers(queenCount, size=queenCount)
        initialPopulationArray.append(queensArray)
    return initialPopulationArray

def selection(population, fitness, k=3):
    rng = np.random.default_rng()
    #select population based on random tournment weighted by fitness
    selection = rng.integers(len(population))
    for i in rng.integers(0, len(population), k-1):
        if fitness[i] < fitness[selection]:
            selection = i
    return population[selection]

def crossover(parent1, parent2, crossoverRate):
    rng = np.random.default_rng()
    parent1, parent2 = np.array(parent1), np.array(parent2)
    child1, child2 = np.array(parent1.copy()), np.array(parent2.copy())
    #check if crossover will happen
    if rng.random() < crossoverRate:
        #select random crossover point that is not the end of array
        crossoverPoint = rng.integers(1, (len(parent1)-1))
        #perform crossover
        child1 = np.append(parent1[:crossoverPoint], parent2[crossoverPoint:])
        child2 = np.append(parent2[:crossoverPoint], parent1[crossoverPoint:])
    return [child1, child2]

def mutation(queensArray, mutationRate):
    rng = np.random.default_rng()
    queensArray = np.array(queensArray)
    for i in range(len(queensArray)):
        # check for a mutation
        if rng.random() < mutationRate:
            #change queen postion to random location
            queensArray[i] = rng.integers(len(queensArray))
    return queensArray

def getFitness(queensArray):
    board = getBoard(queensArray)
    fitnessScore = 0
    fitnessScore = fitnessScore + horizontalCheck(board)
    #redudent due to the queens array only have one queen per colum
    #fitnessScore = fitnessScore + verticalCheck(board)
    fitnessScore = fitnessScore + diagonalCheck(board)
    return fitnessScore

def horizontalCheck(board):
    fitnessScore = 0
    for i in np.array(board).sum(axis=1):
        if i > 1:
            fitnessScore = fitnessScore + i - 1
    return fitnessScore

#redudent due to the queens array only have one queen per colum
def verticalCheck(board):
    fitnessScore = 0
    for i in np.array(board).sum(axis=0):
        if i > 1:
            fitnessScore = fitnessScore + i - 1
    return fitnessScore

def diagonalCheck(board):
    board = np.array(board)
    fitnessScore = 0
    #create a seperate array that is used as index to find the sum of diagonals
    rows, cols = board.shape
    boardRows = np.arange(rows)
    boardCols = np.arange(cols)
    diagonalIndex = boardRows[:, None] - (boardCols - (cols - 1))
    #calculate sums using diagonal index array over the board
    diagonalSums = np.bincount(diagonalIndex.ravel(), weights=board.ravel())
    for i in diagonalSums:
        if i > 1:
            fitnessScore = fitnessScore + i - 1
    #rotate the board array 90 degrees to check the opposite diagonal
    diagonalSums = np.bincount(diagonalIndex.ravel(), weights=np.rot90(board).ravel())
    for i in diagonalSums:
        if i > 1:
            fitnessScore = fitnessScore + i - 1
    return fitnessScore

#used to print the board in a nicer layout
def printBoard(queensArray):
    board = getBoard(queensArray)
    ones = np.ones(8)
    queensArray1Start = np.add(queensArray, ones)
    print(queensArray1Start, end=" Fitness: ")
    print(getFitness(queensArray))
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] == 1:
                print("[Q]", end='')
            else:
                print("[ ]", end='')
        print()
    print()

def geneticAlgorithm(generations, crossoverRate, mutationRate, iteration):
    #create random population of queens
    PopulationArray = np.array(initializePopulation(16, 8)) 

    bestFitness = 100
    bestQueens = np.zeros(shape=(len(PopulationArray[0])))
    for gen in range(generations):
        #create list of all children fitness
        fitness = [getFitness(f) for f in PopulationArray]
        for i in range(len(fitness)):
            if fitness[i] < bestFitness:
                bestFitness = fitness[i]
                bestQueens = np.array(PopulationArray[i])
        #If any reach 0 fitness end generations loop
        if bestFitness == 0:
            break
        
        #create semi ordered list based on the selection function 
        parents = np.array([selection(PopulationArray, fitness) for _ in range(len(PopulationArray))])

        #create a children list and populate using parents that have been crossover and mutated
        children = list()
        for i in range(0, len(PopulationArray), 2):
            parent1, parent2 = parents[i], parents[i+1]
            
            for c in crossover(parent1, parent2, crossoverRate):
                child = mutation(c, mutationRate)
                children.append(child)

        PopulationArray = children
    
    #only if the generation has reached 0 fitness save the solution
    if bestFitness == 0:
        ones = np.ones(8)
        print("\nsolution Found! Iteration: " + str(iteration))
        printBoard(bestQueens)
        return np.add(bestQueens, ones)