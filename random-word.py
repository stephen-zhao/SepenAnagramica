import random


nWords = 3

WORDS_FILE = 'sa0.dat'
g_lsWordsData = []
words = []

with open(WORDS_FILE, 'r') as wordFile:
    for line in wordFile:
        lsWords = list(map(lambda x: x[:-1], line.split()))
        ##### DEBUG USE: print(lsWords[0:10])
        for word in lsWords:
            g_lsWordsData.append(word)
for i in range(nWords):
    words.append(random.choice(g_lsWordsData))

print(str(words))
