import sys
import random
import math

VerboseFlag = True
alphabet = []




class State:
    m_EmissionProbs = {}
    m_TransitionProbs = {}
    index = 0
    Pi = 0
    def __init__(self, EP, TP, idx):
        self.m_EmissionProbs = EP
        self.m_TransitionProbs = TP
        self.index = idx
        self.Pi = 0

    def __initEP__(self, alphabet):
        p = 1
        for i, c in enumerate(alphabet):
            if i == len(alphabet) -1:
                self.m_EmissionProbs[c] = p
            elif c not in self.m_EmissionProbs:
                self.m_EmissionProbs[c] = random.uniform(0, p)
                p -= self.m_EmissionProbs[c]


    def __initTP__(self, States):
        p = 1
        for s in States:
            if s == States[-1]:
                self.m_TransitionProbs[s] = p
            else:
                self.m_TransitionProbs[s] = random.uniform(0,p)
                p -= self.m_TransitionProbs[s]


    def __initRand__(self, alphabet, States):
        self.__initTP__(States)
        self.__initEP__(alphabet)
        self.index = 0

def Forward(States,thisword):
    Alpha= {}
    for s in States:
        Alpha[(s,1)] = s.Pi
    for t in range(2,len(thisword)+2):
        for to_state in States:
            Alpha[(to_state,t)] = 0
            for from_state in States:
                Alpha[(to_state,t)] += Alpha[(from_state,t-1)] * from_state.m_EmissionProbs[thisword[t-2]] * from_state.m_TransitionProbs[to_state]
    return Alpha


def Backward( States, thisword):
    Beta = {}
    last = len(thisword) + 1
    for s in States:
        Beta[(s, last)] = 1
    for t in range(len(thisword),0,-1):
        for from_state in States:
            Beta[(from_state,t)] = 0
            for to_state in States:
                Beta[(from_state,t)] += Beta[(to_state,t+1)] * from_state.m_EmissionProbs[thisword[t-1]] * from_state.m_TransitionProbs[to_state]
    return Beta


def Initialization(n, alphabet):
    if VerboseFlag:
        print("---------------------------")
        print("-  Initialization         -")
        print("---------------------------")

    states = []

    for i in range(n):
        state = State({}, {}, i)
        state.__initEP__(alphabet)
        states.append(state)




    for i in range(n):
        states[i].__initTP__(states)
        if VerboseFlag:
            print("Creating State ", i)
            print("Transitions")

            for j in range(len(states)):
                print("     To state    ", j, "     ", states[i].m_TransitionProbs[states[j]])

            print()
            print("Emission probabilities")
            a = 0
            for c, p in states[i].m_EmissionProbs.items():
                a += p
                print("     Letter      ", c, "     ", p)
            print("Total:   ", a, "\n")



    if VerboseFlag:

        print("-----------------------------")
        print("Pi:")
    p = 1
    for s in states:
        if s == states[-1]:
            s.Pi = p
        else:
            s.Pi = random.uniform(0, p)
            p -= s.Pi
        if VerboseFlag:
            print("State   ", s.index, "    ", s.Pi)
    print()
    with open('localmaxima', 'a') as f:
        f.write("State" + str(states[0].index) + " To State: " + str(states[0].index) + " Prob: " + str(states[0].m_TransitionProbs[states[0]])+ "\n")
        f.write("State" + str(states[0].index) + " To State: " + str(states[1].index) + " Prob: " + str(states[0].m_TransitionProbs[states[1]])+ "\n")
        f.write("State" + str(states[1].index) + " To State: " + str(states[0].index) + " Prob: " + str(states[1].m_TransitionProbs[states[0]])+ "\n")
        f.write("State" + str(states[1].index) + " To State: " + str(states[1].index) + " Prob: " + str(states[1].m_TransitionProbs[states[1]])+ "\n")
    return states

def retT(alpha):
    (s,t) , v = alpha
    return t

def retS(alpha):
    (s,t) , v = alpha
    return s.index

def retKeySC(SC):
    (l, t, f) , v = SC
    return l

def retLet(EP):
    l, v = EP
    return v
def alphaLine(states, line):
    Alpha = Forward(states, line)
    ai = sorted(Alpha.items(), key=retS)
    ai = sorted(ai, key=retT)
    alphaline = ai[len(ai) - 1][1] + ai[len(ai) - 2][1]

    if VerboseFlag:
        for (key, time), value in ai:
            print("State: ", states.index(key), "t: ", time, "Alpha: ", value)

        print("\n", "String probability from Alphas:      ", alphaline, "\n")
    return alphaline, Alpha

def betaLine(states,line):
    Beta = Backward(states, line)
    bi = sorted(Beta.items(), key=retS)
    bi = sorted(bi, key=retT)
    betaline = (bi[0][1] * bi[0][0][0].Pi) + (bi[1][1] * bi[1][0][0].Pi)

    if VerboseFlag:
        for (key, time), value in bi:

            print("State: ", states.index(key), "t: ", time, "Beta: ", value)

        print("\n", "String probability from Betas:      ", betaline, "\n")

    return betaline, Beta

def lineProbs(states):
    with open(sys.argv[1]) as file:
        plogs = 0
        for line in file:
            line = line.strip()
            if VerboseFlag:
                print("----------WORD-----------")
                print( line)
                print("--------------------------")
            alphaline, alphas = alphaLine(states, line)
            betaline, betas = betaLine(states, line)

            plog = -1 * math.log(alphaline, 2)
            plogs += plog
            if VerboseFlag:
                print("plog:", plog)
                print("plog sum: ", plogs)
    return plogs

def softCount(states, initial):
    if VerboseFlag:
        print("---------------------------")
        print("-  Soft Counts Table       -")
        print("---------------------------")
    softcountsTable = {}
    with open(sys.argv[1]) as file:
        for line in file:
            if initial:
                line = line[0]
            else:
                line = line.strip() + "#"
            if VerboseFlag:
                print("-------------- LINE ------------------")
                print(line)
                print("--------------------------------------")
            alphaline, alphas = alphaLine(states, line)
            betaline, betas = betaLine(states, line)

            for (state_i, t_i), alpha in alphas.items():
                for (state_j, t_j) in alphas:
                    if t_i != len(line)+1 and t_j == t_i+1:
                        value = (alpha * state_i.m_EmissionProbs[line[t_i-1]] *
                              state_i.m_TransitionProbs[state_j] * betas[(state_j), t_i+1]) / alphaline

                        sc = (line[t_i-2], state_i.index, state_j.index)

                        if sc in softcountsTable:
                            softcountsTable[sc] += value
                        else:
                            softcountsTable[sc] = value




                        if VerboseFlag:
                            print('Letter: ' + sc[0] + "     From State: " + str(state_i.index) + "     To State: " + str(state_j.index)+ " Soft Count: " +  str(value))

    if VerboseFlag:
        print(" EXPECTED COUNTS TABLE (SO FAR)")

        for (letter, fromS, toS), value in sorted(softcountsTable.items(), key = retKeySC):
            print("Letter:  " + str(letter) + "  From State:  " +
                  str(fromS) + "  To State:  " + str(toS) + " Soft Count:  " + str(value))

    return softcountsTable

def transitionProb(softcountsTable, fromI, toI):
    numerator = 0
    denomenator = 0
    for item in softcountsTable.items():
        (letter, fromSC, toSC) , value = item
        if fromSC == fromI and toSC == toI:
            numerator += value
        if fromSC == fromI:
            denomenator += value

    return (numerator/denomenator)


def initProb(softcountsTable, Z, fromI):
    isc = 0
    for item in softcountsTable.items():
        (letter, fromSC, toSC), value = item
        if fromI == fromSC:
            isc += value
    return (isc/Z)

def emissionsProb(softcountsTable, letter, fromI):
    numerator = 0
    denominator = 0
    for item in softcountsTable.items():
        (letterSC, fromSC, toSC) , value = item
        if fromSC == fromI and letterSC == letter:
            numerator += value
        if fromI == fromSC:
            denominator += value
    return (numerator/denominator)

def updateStates(states, softcountTableInit, softcountTable, Z):
    if  VerboseFlag:
        print("----------------------------")
        print("      Iteration Summary     ")
        print("----------------------------")

    for state in states:
        if VerboseFlag:
            print("From State:  " + str(state.index))
            #update the transition probability
            print("Transition probabilities")
        for toS, prob in state.m_TransitionProbs.items():
            state.m_TransitionProbs[toS] = transitionProb(softcountTable, state.index, toS.index)
            if VerboseFlag:
                print("To State:  " + str(toS.index) + "  prob: " + str(state.m_TransitionProbs[toS]))

        #update emission probability
        if VerboseFlag:
            print("Emission probabilities")

        for letter, prob in state.m_EmissionProbs.items():
            state.m_EmissionProbs[letter] = emissionsProb(softcountTable, letter, state.index)

            if VerboseFlag:
                print(letter + "   prob: " + str(state.m_EmissionProbs[letter]))

        #update the initial pi
        state.Pi = initProb(softcountTableInit, Z, state.index)
        if VerboseFlag:
            print("State: " + str(state.index) + "  Pi: " + str(state.Pi))

def logRatios(states):
    logratios = {}
    for letter, value in states[0].m_EmissionProbs.items():
        logratios[letter] = value/ states[1].m_EmissionProbs[letter]
        logratios[letter] = math.log(logratios[letter], 2)
    if VerboseFlag:
        print('-' * 45)
        print('Log Ratio of emissions from 2 states:')
        print('-' * 45 + '\n')
        for letter, value in sorted(logratios.items(), key = retLet):
            print ("Letter: " + letter +     " Value:  " + str(value))

        return logratios


def main():

    orig_stdout = sys.stdout
    f = open('out.txt', 'w')
    sys.stdout = f
    global VerboseFlag
    if sys.argv[2] == '-v':
        VerboseFlag= True
    else:
        VerboseFlag = False

    doI = False
    iterations = 0
    if int(sys.argv[3]) > 0:
        doI = True
        iterations = sys.argv[3]

    states = []
    with open(sys.argv[1]) as file:
        Z = 0
        for line in file:
            Z +=1
            #determine the alphabet
            for c in line:
                if c.isspace():
                    c = '#'
                if c not in alphabet:
                    alphabet.append(c)


    states = Initialization(2, alphabet)
    plogs = lineProbs(states)
    softcountTable = softCount(states, False)
    softcountTableInit =  softCount(states, True)
    updateStates(states, softcountTableInit, softcountTable, Z)
    VerboseFlag = False
    plogdif = 400

    print("Initial Plog Sum: " + str(plogs))


    if doI:
        for i in range(iterations):
            if i == iterations-1:
                VerboseFlag = True
                print("========= FINAL ITERATION ========")
            cplogs = lineProbs(states)
            plogdif = plogs - cplogs
            plogs = cplogs
            print("Plog of Iteration: " + str(plogs) + " Plog Dif: " +str(plogdif))
            softcountTable = softCount(states, False)
            softcountTableInit = softCount(states, True)
            updateStates(states, softcountTableInit, softcountTable, Z)

    else:
        while math.fabs(plogdif) >= .02:

            cplogs = lineProbs(states)
            plogdif = plogs - cplogs
            if math.fabs(plogdif) < .02:
                VerboseFlag = True
                print("========= FINAL ITERATION ========")
            plogs = cplogs
            print("Plog of Iteration: " + str(plogs) + " Plog Dif: " + str(plogdif))
            softcountTable = softCount(states, False)
            softcountTableInit = softCount(states, True)
            updateStates(states, softcountTableInit, softcountTable, Z)

            if math.fabs(plogdif) < .02:
                logRatios(states)
                with open('localmaxima', 'a') as f:
                    f.write("Final Iteration's Plog Sum: "+ str(plogs)+ "\n"*2)

    sys.stdout = orig_stdout
    f.close()
if __name__ == '__main__':
    main()


