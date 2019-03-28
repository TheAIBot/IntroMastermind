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


BLACKP = 0
WHITEP = 1

#Board
ncolor = 6
npos = 4
colors = np.arange(ncolor)
#Functions


##  Output funtion
def Feedback(answer, guess):
    feedback = [0, 0]
    colorsInGuess = set()
    colorsInAnswer = []
    positionsOfCorrectColors = []
    for i in range(len(guess)):
        if guess[i] == answer[i]:
            feedback[BLACKP] += 1
            positionsOfCorrectColors.append(i)
        else:
            colorsInGuess.add(guess[i])
            colorsInAnswer.append(answer[i])
    for i in colorsInGuess:
        if i in colorsInAnswer:
            feedback[WHITEP] += 1
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
        if feedback[0] != pegs[0] or feedback[1] != pegs[1]:
            numberOfDeletedGuesses += 1
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
def bestGuess(SearchSpace):
    print('s')
    bestG = np.array([])
    minimaxDeletedStates = 0
    S = SearchSpace
    for i in SearchSpace:
        minDeletedStates = 1296
        for j in range(npos+1):
            for k in range(npos+1-j):
                O = np.array([j, k])
                deletedStates = pruneValidGuessesGetNumberOfDeletedGuesses(i,O,S)
                if(deletedStates < minDeletedStates ):
                    minDeletedStates  = deletedStates
        if(minDeletedStates > minimaxDeletedStates):
            minimaxDeletedStates = minDeletedStates 
            bestG = i
    return(bestG)

StateSpace = np.ones((ncolor**npos,npos), dtype=int) #Full State Space
createStateSpace(StateSpace, npos, 0, [])


#Play the game
Iteration=np.zeros(10)
for l in range(10):         
    S=StateSpace[:,:]                                   #Search Space
    CODE=S[random.randint(0,len(S)-1),:]        # Random CODE
    #print(CODE)
    #CODE=np.array([1,0,2,4])
    guessIndex = random.randint(0,len(S)-1)
    #F=bestGuess(S)  #Initial Guess
    F=S[guessIndex,:].tolist()  #Initial Guess
    F=np.array([0,0,1,1])
    n=1
    O=Feedback(CODE, F)
    while O[BLACKP] != npos:
        guessIndex=int(np.where(np.all(S==F,axis=1))[0])
        S=RemoveIndex(guessIndex, S) #Removing Guess From SearchSpace
        S=pruneValidGuesses(F,O,S)
        #print(F,O,len(S))
        #guessIndex = random.randint(0,len(S)-1)
        if len(S) == 1:
            F=S[0]
        else:
            F=bestGuess(S) #New Guess
        #print('NewGuess',F,'SizeSearchSpace',len(S))
        #F=S[guessIndex,:].tolist() #New Guess
        O=Feedback(CODE, F)                                #Output from guess     
        n+=1                                       #Iteration Counter
        if O[0] == 4:
            #print('solution',F,'Pegs',Feedback(CODE, F),'Guesses',n,'ShapeSolutionSpace',np.shape(S),l) #Printing result
            break #Starting new game
    Iteration[l]=n
#Result
print(round(np.average(Iteration),2),sum(Iteration),max(Iteration))

#TIME
elapsed_time = time.process_time() - tid
print('Time:',round(elapsed_time,2),'s','Time pr game:',round(elapsed_time/(l+1),2),'s')
# Guess with MinMax 4.46 223.0 6.0
# Random Guesses 4.76 238.0 6.0 
