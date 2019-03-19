import random
import heapq

class State:
    def __init__(self, game, parent, possibleColumnColors, stateSpace, validStatesCount, guess, blackpegPositions):
        self.game = game
        self.parent = parent
        self.possibleColumnColors = possibleColumnColors
        self.stateSpace = stateSpace
        self.validStatesCount = validStatesCount
        self.guess = guess
        self.blackPegPositions = blackpegPositions

    def GetChildren(self, pegs):
        ccp = pegs[0]
        ccnp = pegs[1]

        children = []
        blackPegPoses = []
        for x in range(0, self.game.columnCount):
            blackPegPoses.append(False)

        self.GetAllPossibleBlackPegsPositionChildren(children, blackPegPoses, 0, ccp, ccnp)
        return children

    def GetAllPossibleBlackPegsPositionChildren(self, children, blackPositions, columnIndex, ccp, ccnp):
        if columnIndex == self.game.columnCount:
            stateCopy = self.Copy()
            stateCopy.RemoveInvalidStates(blackPositions, ccnp)
            if stateCopy.validStatesCount == 0:
                return
            stateCopy.guess = stateCopy.GetRandomGuessFromStateSpace()
            stateCopy.blackPositios = blackPositions.copy()
            stateCopy.parent = self
            children.append(stateCopy)
            return

        if ccp > 0:
            blackPositions[columnIndex] = True
            self.GetAllPossibleBlackPegsPositionChildren(children, blackPositions, columnIndex + 1, ccp - 1, ccnp)
            blackPositions[columnIndex] = False

        self.GetAllPossibleBlackPegsPositionChildren(children, blackPositions, columnIndex + 1, ccp, ccnp)

    def Copy(self):
        pcCopy = []
        ssCopy = self.stateSpace.copy()
        gCopy = self.guess.copy()

        for x in range(0, len(self.possibleColumnColors)):
            pcCopy.append(self.possibleColumnColors[x].copy())

        return State(self.game, self.parent, pcCopy, ssCopy, self.validStatesCount, gCopy, self.blackPegPositions.copy())

    def RemoveInvalidStates(self, blackPegPositions, ccnp):
        if ccnp == self.game.columnCount:
            stateIndex = self.GuessToStateIndex(self.guess)
            self.stateSpace[stateIndex] = False
        else:
            isColumnColorTaken = blackPegPositions.copy()
            self.RemoveAllColorCombinations(isColumnColorTaken, blackPegPositions, 0, 0)




    def RemoveAllColorCombinations(self, isColumnColorTaken, blackPositions, columnIndex, stateIndex):
        #Stop recorsion if it has gone through all the columns.
        #Now remove the state
        if columnIndex == self.game.columnCount:
            #Only decrease if it was valid to begin with
            if self.stateSpace[stateIndex]:
                self.validStatesCount = self.validStatesCount - 1
            self.stateSpace[stateIndex] = False
            return

        #If a black pegs resides here then go through
        #all the incorrect colors instead
        if blackPositions[columnIndex]:
            isColumnColorTaken[columnIndex] = True
            for x in range(0, self.game.colorCount):
                if x != self.guess[columnIndex]:
                    partialIndex = x * (self.game.colorCount ** columnIndex)
                    self.RemoveAllColorCombinations(isColumnColorTaken, blackPositions, columnIndex + 1, stateIndex + partialIndex)
            isColumnColorTaken[columnIndex] = False


        for x in range(0, len(isColumnColorTaken)):
            if not isColumnColorTaken[x]:
                isColumnColorTaken[x] = True
                partialIndex = self.guess[x] * (self.game.colorCount ** columnIndex)
                self.RemoveAllColorCombinations(isColumnColorTaken, blackPositions, columnIndex + 1, stateIndex + partialIndex)
                isColumnColorTaken[x] = False

    def GuessToStateIndex(self, g):
        index = 0
        for x in range(0, len(g)):
            index = index + g[x] * (self.game.colorCount ** x)
        return index;

    def GetRandomGuessFromStateSpace(self):
        guessesToIngore = random.randint(0, self.validStatesCount // 2)
        for x in range(0, len(self.stateSpace)):
            if self.stateSpace[x]:
                return self.IndexToGuess(x)
                #if guessesToIngore > 0:
                #    guessesToIngore = guessesToIngore - 1
                #else:
                #    return self.IndexToGuess(x)
        if True:
            pass

    def IndexToGuess(self, index):
        g = []
        while index > 0:
            g.append(index % self.game.colorCount)
            index = index // self.game.colorCount

        while len(g) < self.game.columnCount:
            g.append(0)

        return g


    def __hash__(self):
        result = 1
        #for x in range(0, len(self.guess)):
        #    result = 31 * result + self.guess[x]

        for x in range(0, len(self.stateSpace)):
            if self.stateSpace[x]:
                result = 31 * result + 2
            else:
                result = 31 * result + 1
        result = 31 * result + self.validStatesCount

        for x in range(0, len(self.possibleColumnColors)):
            for y in range(0, len(self.possibleColumnColors[x])):
                if self.possibleColumnColors[x][y]:
                    result = 31 * result + 2
                else:
                    result = 31 * result + 1
        return result

    def __eq__(self, other):
        #if self.guess != other.guess:
        #    return False;
        if self.validStatesCount != other.validStatesCount:
            return False
        if self.stateSpace != other.stateSpace:
            return False
        if self.possibleColumnColors != other.possibleColumnColors:
            return False
        return True

    def __lt__(self, other):
        return self.validStatesCount < other.validStatesCount

class StateGroup:
    def __init__(self, states):
        self.states = states

class Game:
    def __init__(self, colorCount, columnCount):
        self.colorCount = colorCount
        self.columnCount = columnCount
        self.correctGuess = self.GetRandomGuess()

    def GetRandomGuess(self):
        guess = []
        for x in range(0, self.columnCount):
            guess.append(random.randint(0, self.colorCount - 1))

        return guess
    
    def GetRandomInitialState(self):
        #Create state space.
        #All states are valid to begin with.
        stateSpace = []
        for x in range(0, self.colorCount ** self.columnCount):
            stateSpace.append(True)

        #Create the possible colors for each column.
        #To begin with all colors ar allowed.
        possibleColumnColors = []
        for x in range(0, self.columnCount):
            possibleColumnColors.append([])
            for y in range(0, self.colorCount):
                possibleColumnColors[x].append(True)

        blackPegPositions = []
        for x in range(0, self.columnCount):
            blackPegPositions.append(False)

        guess = self.GetRandomGuess()
        return State(self, None, possibleColumnColors, stateSpace, len(stateSpace), guess, blackPegPositions)

    def IsGoalState(self, state):
        return state.validStatesCount == 1

    def GetPegs(self, guess):
        ccp = 0
        ccnp = 0

        guessCopy = guess.copy()
        correctGuessCopy = self.correctGuess.copy()

        #Go through each column and check if the
        #color is correct. Remove correct colors
        #from the guess and answer to avoid
        #duplicate pegs if the answer or guess
        #has more than one of the same color in it
        for x in range(0, len(guess)):
            if guess[x] == self.correctGuess[x]:
                ccp = ccp + 1
                guessCopy.remove(guess[x])
                correctGuessCopy.remove(guess[x])

        #Go through each color in the guess
        #and check if the color exists in the answer
        for x in range(0, len(guessCopy)):
            for y in range(0, len(correctGuessCopy)):
                if guessCopy[x] == correctGuessCopy[y]:
                    ccnp = ccnp + 1
                    correctGuessCopy.remove(guessCopy[x])
                    break

        return [ccp, ccnp]

def Search(game: Game):
    expandedSet = set()
    frontierSet = set()
    frontier = []
    
    initialState = game.GetRandomInitialState()
    heapq.heappush(frontier, initialState)
    frontierSet.add(initialState)

    while True:
        if len(frontier) == 0:
            return False

        leaf = heapq.heappop(frontier)
        frontierSet.remove(leaf)
        expandedSet.add(leaf)

        if game.IsGoalState(leaf):
            return leaf

        #print(leaf.guess)
        pegs = game.GetPegs(leaf.guess)
        #print(pegs)

        for child in leaf.GetChildren(pegs):
            if not child in frontierSet and not child in expandedSet:
                heapq.heappush(frontier, child)
                frontierSet.add(child)

    return false

#game = Game(6, 4)
#game.correctGuess = [1,2,2,3]
#print(game.GetPegs([1,1,5,6]))

for x in range(0, 100):
    game = Game(6, 4)
    endState = Search(game)
    length = 0
    while endState.parent is not None:
        length = length + 1
        endState = endState.parent
    print(length)


game = Game(6, 4)
endState = Search(game)
while endState.parent is not None:
    print(endState.guess)
    endState = endState.parent