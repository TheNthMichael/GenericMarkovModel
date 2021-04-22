from struct import Struct
from random import randint
import winsound
import wave
import numpy as np


"""
Symbol Table Representation (Brute force wrt memory):
[KGRAM ][FREQ ][ALPHABETFREQ: a1, a2, a3, ...]
[KGRAM1][FREQ1][a11, a21, a31, a41, a51, ... ]
[KGRAM2][FREQ2][a12, a22, a32, a42, a52, ... ]
[KGRAM3][FREQ3][a13, a23, a33, a43, a53, ... ]

For each KGRAM found in the original text, count the frequency of it, and note the frequency of the character following that KGRAM.

dictionary<string>[KGRAM] = {
    KGRAM_FREQUENCY,
    dictionary<char> = {
        'char' : frequency
    }
}

"""

class KGramEntry:
        def __init__(self, frequency):
            self.frequency = frequency
            self.alphabet = {}

class MarkovModel:

    def __init__(self, k):
        self.kgrams = k
        self.symbolTable = {}

    """
    Returns the frequency for a given kgram.
    Returns 0 if kgram DNE
    """
    def kgramFrequency(self, kgram):
        if not kgram in self.symbolTable:
            return 0
        else: 
            return self.symbolTable[kgram].frequency

    """
    Returns the frequency of a character occuring after a given kgram.
    Returns 0 if character DNE
    """
    def kgramCharacterFrequency(self, kgram, character):
        if not character in self.symbolTable[kgram].alphabet:
            return 0
        else:
            return self.symbolTable[kgram].alphabet[character]
    
    """
    Adds the given information to the symbol table => works by looping over circularly (although this may not be optimal)
    Information is an array of characters in the alphabet.
    """
    def addInformation(self, information, looping=True):
        print("Adding information...")
        # if we are not allowing circular use of the information.
        infoCount = len(information)
        if not looping:
            if self.kgrams > infoCount:
                raise Exception("Error, {self.kgrams} > {infoCount}.")
            else:
                # generate all kgrams
                for i in range(infoCount):
                    # kgram not possible in this state.
                    if infoCount - i < self.kgrams:
                        break

                    # generate kgram
                    kgram = []
                    for j in range(self.kgrams):
                        kgram.append(information[(i + j)])

                    # get the character following the previous kgram.
                    nextCharacter = information[(i + self.kgrams) % infoCount]
                    tkgram = tuple(kgram)
                    # check if kgram is in symbol table
                    if tkgram in self.symbolTable:
                        self.symbolTable[tkgram].frequency += 1
                        # check if character is in alphabet
                        if nextCharacter in self.symbolTable[tkgram].alphabet:
                            self.symbolTable[tkgram].alphabet[nextCharacter] += 1
                        else:
                            self.symbolTable[tkgram].alphabet[nextCharacter] = 1
                    else:
                        self.symbolTable[tkgram] = KGramEntry(1)
                        self.symbolTable[tkgram].alphabet[nextCharacter] = 1
        # case here looping is allowed
        else:
            # generate all kgrams
            for i in range(len(information)):
                # generate kgram
                kgram = []
                for j in range(self.kgrams):
                    kgram.append(information[(i + j) % len(information)])
                    
                # get the character following the previous kgram.
                nextCharacter = information[(i + self.kgrams) % len(information)]
                tkgram = tuple(kgram)
            # check if kgram is in symbol table
                if tkgram in self.symbolTable:
                    self.symbolTable[tkgram].frequency += 1
                    # check if character is in alphabet
                    if nextCharacter in self.symbolTable[tkgram].alphabet:
                        self.symbolTable[tkgram].alphabet[nextCharacter] += 1
                    else:
                        self.symbolTable[tkgram].alphabet[nextCharacter] = 1
                else:
                    self.symbolTable[tkgram] = KGramEntry(1)
                    self.symbolTable[tkgram].alphabet[nextCharacter] = 1
        print("done!")

    """
    Returns a random character that follows the given kgram based on the frequency of the character in the symbol table.
    """
    def kRand(self, kgram):
        n = randint(0, self.symbolTable[kgram].frequency - 1)
        lowerBound = 0
        upperBound = 0
        for e in self.symbolTable[kgram].alphabet:
            upperBound += self.symbolTable[kgram].alphabet[e]
            if lowerBound <= n and n < upperBound and upperBound != lowerBound:
                return e
            lowerBound = upperBound
        raise Exception("Probability bounds checking failed.")

    """
    Returns pseudo text generated from markov model.
    """
    def generateText(self, kgram, amount):
        if len(kgram) != self.kgrams:
            raise Exception("Kgram needs to be of size " + str(len(kgram)))
        if amount < self.kgrams:
            raise Exception("More text needed for generating")
        if not tuple(kgram) in self.symbolTable:
            raise Exception("{kgram} not in symbol table")
        
        result = []
        for x in kgram:
            result.append(x)
        for i in range(amount - self.kgrams):
            character = self.kRand(tuple(kgram))
            result.append(character)
            if self.kgrams != 0:
                kgram = kgram[1:self.kgrams]
                kgram.append(character)

        return result


def start():
    """
    model = MarkovModel(6)
    info = "hello this is a test of strings I wonder if it will work?"
    model.addInformation(list(info))
    starter = list("hello ")
    res = model.generateText(starter, 60)
    st = ""
    for x in res:
        st += x
    print(st)
    """
    data = wave.open("Barry.wav", 'rb')
    seconds = 20
    kgramsize = 13
    model = MarkovModel(kgramsize)
    soundwave = data.readframes(seconds * data.getframerate())
    info = np.frombuffer(soundwave, dtype='int16')
    info = [x for x in info if x != 0]
    print(info[0:10])
    print(len(info[0:1000000]))
    model.addInformation(info[0:1000000], looping=True)

    # Brian
    data2 = wave.open("Brian.wav", 'rb')
    soundwave2 = data2.readframes(seconds * data2.getframerate())
    info2 = np.frombuffer(soundwave2, dtype='int16')
    info2 = [x for x in info2 if x != 0]
    print(info2[0:10])
    print(len(info2[0:1000000]))
    model.addInformation(info2[0:1000000], looping=True)

    starter = info[0:kgramsize]
    res = model.generateText(list(starter), 20 * data.getframerate())
    output = wave.open("Output.wav", 'wb')
    output.setnchannels(data.getnchannels())
    output.setsampwidth(data.getsampwidth())
    output.setframerate(data.getframerate())
    for x in res:
        output.writeframes(Struct('h').pack(x))
    output.close()

    


if __name__ == '__main__':
    start()
