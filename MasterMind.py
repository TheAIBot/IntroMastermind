#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 10:48:59 2019
@author: jonatan
"""
import numpy as np
import random
import time
import sys


tid = time.process_time()

#arr = np.array([[1],[2],[3],[4],[5],[6],[7],[8]])
#print(arr)
#toDelete = [0, 3, 6]
#arr = np.delete(arr, toDelete, 0)
#print(arr)

#print((np.array([1,2,2,4]) == [3,2,5,2]).sum())

#sys.exit("Error message")


BLACKP = 0
WHITEP = 1

#Board
ncolor = 6
npos = 4
colors = np.arange(ncolor)
#Functions

def sumEquals(a, b):
    s = 0
    for i in range(len(a)):
        if a[i] == b[i]:
            s = s + 1
    return s

def sumSame(a, b):
    s = 0
    for i in range(len(a)):
        if a[i] == b:
            s = s + 1
    return s

##  Output funtion
def Feedback(answer, guess): 
    feedback = [0, 0]
    colorsInGuess = set()
    for i in range(len(guess)):
        if guess[i] == answer[i]:
            feedback[BLACKP] += 1
        else:
            colorsInGuess.add(guess[i])
    for i in colorsInGuess:
        if i in answer:
            feedback[WHITEP] += 1


    #feedback[BLACKP] = sumEquals(answer, guess) # BLACK pegs
    #for color in colors:          # White pegs
    #    colorOccurencesInGuess  = sumSame(guess, color)
    #    colorOccurencesInAnswer = sumSame(answer, color)
    #    if colorOccurencesInAnswer > 0 and colorOccurencesInGuess > 0:
    #        if colorOccurencesInGuess <= colorOccurencesInAnswer:
    #            feedback[WHITEP] += colorOccurencesInGuess
    #        if colorOccurencesInGuess > colorOccurencesInAnswer:
    #            feedback[WHITEP] += colorOccurencesInAnswer
    #feedback[WHITEP] -= feedback[BLACKP]          # White pegs minus black pegs avoid double count
    return feedback

##  Deleting by index
def RemoveIndex(index, searchSpace):
    return np.delete(searchSpace, index, 0)

def pruneValidGuesses(Guess, pegs, searchSpace):
    indicesToRemove = []
    for i in range(len(searchSpace)):
        feedback = Feedback(searchSpace[i, :], Guess)
        if feedback[0] != pegs[0] or feedback[1] != pegs[1]:
            indicesToRemove.append(i)     
    searchSpace = np.delete(searchSpace, indicesToRemove, 0)
    return searchSpace 

def pruneValidGuessesGetNumberOfDeletedGuesses(Guess, pegs, searchSpace):
    numberOfDeletedGuesses = 0
    for i in range(len(searchSpace)):
        feedback = Feedback(Guess, searchSpace[i, :])
        print(feedback)
        if feedback[0] != pegs[0] or feedback[1] != pegs[1]:
            numberOfDeletedGuesses += 1
            if numberOfDeletedGuesses == len(searchSpace):
                print("")
    return numberOfDeletedGuesses 

#######################


def createStateSpace(stateSpace, columnsLeft, index, guess):
    if columnsLeft == 0:
        stateSpace[index, :] = guess.copy()
        return index + 1
        
    for i in range(ncolor):
        guess.append(i)
        index = createStateSpace(stateSpace, columnsLeft - 1, index, guess)
        guess.pop()    
    return index

## Calculate the best guess
def bestGuess(SearchSpace, origGuess, origFeedback):
    origFeedbackSum = 0
    if origFeedback is not None:
        origFeedbackSum = origFeedback.sum()
    pr = 0
    bestG = np.array([])
    bestWorstCaseDecreasedSearchSpace = len(SearchSpace)
    for i in range(len(SearchSpace)):
        guess = SearchSpace[i, :].tolist()
        worstCaseDecreasedSearchSpace = 0
        
        guessDifference = npos
        if origGuess is not None:
            guessDifference = npos - sumEquals(origGuess, guess)
        
        for j in range(npos+1):
            for k in range(npos+1-j):
                if abs(origFeedbackSum - (j + k)) < guessDifference:
                    deletedGuesses = pruneValidGuessesGetNumberOfDeletedGuesses(guess, [j, k], SearchSpace)
                    guessesRemaining = len(SearchSpace) - deletedGuesses
                    if guessesRemaining <= 0:
                        print(guessesRemaining)
                    #print(len(S))
                    if(guessesRemaining > worstCaseDecreasedSearchSpace):
                        worstCaseDecreasedSearchSpace = guessesRemaining
        if(worstCaseDecreasedSearchSpace < bestWorstCaseDecreasedSearchSpace):
            bestWorstCaseDecreasedSearchSpace = worstCaseDecreasedSearchSpace
            bestG = guess
    #print('BestGuessThing',bestWorstCaseDecreasedSearchSpace)
        pr += 1
        print(pr)
    return(bestG)

StateSpace = np.ones((ncolor**npos,npos), dtype=int) #Full State Space
createStateSpace(StateSpace, npos, 0, [])


#Play the game
Iteration=np.zeros(100)
for l in range(100):         
    S=StateSpace[:,:]                                   #Search Space
    CODE=S[random.randint(0,len(S)-1),:]        # Random CODE
    #CODE=np.array([1,0,2,4])
    guessIndex = random.randint(0,len(S)-1)
    F=bestGuess(S, None, None)  #Initial Guess
    #F=S[guessIndex,:].tolist()  #Initial Guess
    #F=[2,2,4,4]
    #print('InitialGuess',F)
    n=1
    O=Feedback(CODE, F)
    while O[BLACKP] != npos:
        guessIndex=int(np.where(np.all(S==F,axis=1))[0])
        S=RemoveIndex(guessIndex, S) #Removing Guess From SearchSpace
        S=pruneValidGuesses(F,O,S)
        #guessIndex = random.randint(0,len(S)-1)
        F=bestGuess(S, F, O) #New Guess
        #print('NewGuess',F,'SizeSearchSpace',len(S))
        #F=S[guessIndex,:].tolist() #New Guess
        O=Feedback(CODE, F)                                #Output from guess     
        n+=1                                       #Iteration Counter
        if all(F==CODE):
            print('solution',F,'Pegs',Feedback(CODE, F),'Guesses',n,'ShapeSolutionSpace',np.shape(S),l) #Printing result
            break #Starting new game
    Iteration[l]=n
#Result
print(round(np.average(Iteration),2),sum(Iteration),max(Iteration))

#TIME
elapsed_time = time.process_time() - tid
print('Time:',round(elapsed_time,2),'s','Time pr game:',round(elapsed_time/2,2),'s')
