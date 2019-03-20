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

#sys.exit("Error message")


BLACKP = 0
WHITEP = 1

#Board
ncolor = 6
npos = 4
colors = np.arange(ncolor)
#Functions

##  Output funtion
def Feedback(answer, guess): 
    feedback = np.array([0, 0])
    feedback[BLACKP] = (answer == guess).sum() # BLACK pegs
    for color in colors:          # White pegs
        colorOccurencesInGuess  = (guess  == color).sum()
        colorOccurencesInAnswer = (answer == color).sum()
        if colorOccurencesInAnswer > 0 and colorOccurencesInGuess > 0:
            if colorOccurencesInGuess <= colorOccurencesInAnswer:
                feedback[WHITEP] += colorOccurencesInGuess
            if colorOccurencesInGuess > colorOccurencesInAnswer:
                feedback[WHITEP] += colorOccurencesInAnswer
    feedback[WHITEP] -= feedback[BLACKP]          # White pegs minus black pegs avoid double count
    return feedback

##  Deleting by index
def RemoveIndex(index, searchSpace):
    return np.delete(searchSpace, index, 0)
            

## Transforming Search Space With White PEGS 
def delW1(Guess, pegs, searchSpace):
    if (pegs[WHITEP] != 0) & (pegs[BLACKP] == 0):                             #If there is white pegs and no black
        indicesToRemove = []
        for i in range(len(searchSpace)):   #Going throw states in S
            for k in range(npos):                               #Going throw pos in state
                if searchSpace[i, k] == Guess[k]:                      #If State Has color in same pos as in state it is remove(No black peg)         
                    indicesToRemove.append(i)
                    break
        searchSpace = np.delete(searchSpace, indicesToRemove, 0)
    
    indicesToRemove = []
    pegSum = pegs.sum()
    for i in range(len(searchSpace)):
        if len(set(searchSpace[i, :]).intersection(Guess)) > pegSum:
            indicesToRemove.append(i)  
    return np.delete(searchSpace, indicesToRemove, 0)

def sumEquals(a, b):
    s = 0
    for i in range(len(a)):
        if a[i] == b[i]:
            s = s + 1
    return s

## Transforming Search Space With Black PEGS 
def delB1(guess, pegs, searchSpace):
    if pegs[BLACKP] == 0:                                     # If no black return
        return searchSpace
        
    indicesToRemove = []
    for i in range(len(searchSpace)):   #Going throw states from the bag of SS  
        if not sumEquals(searchSpace[i, :], guess) == pegs[BLACKP]: #With k, Guess 5.15, with pegs 4.6-5.1
            indicesToRemove.append(i)
    return np.delete(searchSpace, indicesToRemove, 0)
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

StateSpace = np.ones((ncolor**npos,npos), dtype=int) #Full State Space
createStateSpace(StateSpace, npos, 0, [])


#Play the game
Iteration=np.zeros(1000)
for l in range(1000):         
    S=StateSpace[:,:]                                   #Search Space
    CODE=S[random.randint(0,len(S)-1),:]        # Random CODE
    F=S[random.randint(0,len(S)-1),:].tolist()  #Initial Guess
    n=1
    O=Feedback(CODE, F)
    while O[BLACKP] != npos:
        S=RemoveIndex(S.tolist().index(F),S) #Removing Guess From SearchSpace
        S=delB1(F,O,S)                 #Acting on Black pegs
        S=delW1(F,O,S)                 #Acting on White pegs
        F=S[random.randint(0,len(S)-1),:].tolist() #New Guess
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
print('Time:',round(elapsed_time,2),'s','Time pr game:',round(elapsed_time/l,2),'s')