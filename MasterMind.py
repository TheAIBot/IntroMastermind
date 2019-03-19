#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 10:48:59 2019

@author: jonatan
"""
import numpy as np
import random
import time

tid = time.process_time()
CODE=np.array([1,3,5,0])

#Board
ncolor=6
npos=4
L=np.arange(ncolor)
#Functions
LoopCounter=np.zeros(7)
##  Output funtion
def Output(X): 
    O=np.array([0,0])
    O[0]=(CODE==X).sum() # BLACK pegs
    for i in L:          # White pegs
        LoopCounter[0]+=1
        if (any(i==CODE)) and (any(i==X)):
            if ((X == i).sum() == (CODE == i).sum()) or ((X == i).sum() <= (CODE == i).sum()):
                O[1]+=(X == i).sum()
            if (X == i).sum() > (CODE == i).sum():
                O[1]+=(CODE == i).sum()
    O[1]-=O[0]          # White pegs minus black pegs avoid double count
    return O

##  Deleting by index
def DelId(Index,SearchSpace):
    return np.delete(SearchSpace, Index, 0)

## Transforming Search Space With White PEGS 
def delW1(Guess,Pegs,SearchSpace):
    if all(Pegs==np.array([0,0])):                                  #Case with no pegs
        for i in np.flip(np.arange(len(SearchSpace), dtype=int)):   #Deleting all solutions containing colors in guess
            LoopCounter[1]+=1
            if len(set(SearchSpace[i,:]).intersection(Guess))>0:
                SearchSpace=DelId(i,SearchSpace)
    if (Pegs[1] != 0) & (Pegs[0] == 0):                             #If there is white pegs and no black
        for i in np.flip(np.arange(len(SearchSpace), dtype=int)):   #Going throw states in S
            LoopCounter[2]+=1
            for k in np.arange(npos):                               #Going throw pos in state
                LoopCounter[3]+=1
                if SearchSpace[i,k]==Guess[k]:                      #If State Has color in same pos as in state it is remove(No black peg)         
                   SearchSpace=DelId(i,SearchSpace)
                   break
    if all(Pegs[1]==np.array([0])):
        return SearchSpace
    for k in np.arange(npos)+1: #Should be last
        LoopCounter[4]+=1
        if all(Pegs[1]==np.array([k])):
            for i in np.flip(np.arange(len(SearchSpace), dtype=int)):
                LoopCounter[5]+=1
                if len(set(SearchSpace[i,:]).intersection(Guess))>(k+Pegs[0]):
                    SearchSpace=DelId(i,SearchSpace)          
    return SearchSpace

## Transforming Search Space With Black PEGS 
def delB1(Guess,Pegs,SearchSpace):
    if all(Pegs[0]==np.array([0])):                                     # If no black return
        return SearchSpace
    for i in np.flip(np.arange(len(SearchSpace), dtype=int)):   #Going throw states from the bag of SS
            LoopCounter[6]+=1    
            if not (SearchSpace[i,:]==Guess).sum()==Pegs[0]: #With k, Guess 5.15, with pegs 4.6-5.1
                    SearchSpace=DelId(i,SearchSpace)
    return SearchSpace
#######################
SS=np.ones((ncolor**npos,npos), dtype=int) #Full State Space
q=0
for i in L:
    for p in L:
        for j in L:
            for k in L:
                SS[q,:]=[i,p,j,k]
                q=q+1 
#Play the game
Iteration=np.zeros(50)
for l in np.arange(50):         
    S=SS[:,:]                                   #Search Space
    CODE=S[random.randint(0,len(S)-1),:]        # Random CODE
    F=S[random.randint(0,len(S)-1),:].tolist()  #Initial Guess
    n=1
    O=Output(F)
    while O[0]!=4:
        S=DelId(S.tolist().index(F),S) #Removing Guess From SearchSpace
        S=delW1(F,O,S)                 #Acting on White pegs
        S=delB1(F,O,S)                 #Acting on Black pegs
        F=S[random.randint(0,len(S)-1),:].tolist() #New Guess
        O=Output(F)                                #Output from guess     
        n+=1                                       #Iteration Counter
        if all(F==CODE):
            print('solution',F,'Pegs',Output(F),'Guesses',n,'ShapeSolutionSpace',np.shape(S),l) #Printing result
            break #Starting new game
    Iteration[l]=n
#Result
print(round(np.average(Iteration),2),sum(Iteration),max(Iteration))

#TIME
elapsed_time = time.process_time() - tid
print('Time:',round(elapsed_time,2),'s','Time pr game:',round(elapsed_time/l,2),'s')