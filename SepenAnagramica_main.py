# Stephen Zhao (www.zhaostephen.com)
# SepenAnagramica v0.1.0
# 2015-06-05
#
# Copyright (C) 2015  Stephen Zhao
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#############################################################
#========================= Includes =========================
#############################################################
import random
from threading import Thread
import time
import xml.etree.ElementTree as ET

#############################################################
#======================== Global Var ========================
#############################################################
DATA_FILE = "sa1.dat"
WORDS_FILE = "sa2.dat"
CONFIG_FILE = "sa3.dat"
LICENSE_FILE = "LICENSE.TXT"
README_FILE = "README.TXT"
GAME_QUIT = 10001
GAME_WIN = 10002
GAME_LOSE = 10003
TEXT = {}
CONFIG = {}
    
g_bIsDone = False
g_bIsDoneGame = False
g_timer = 0
g_lsWordsData = []
g_lsbGameData = []
g_lchGameLetters = []
g_bDebugMode = False

#############################################################
#====================== Util Functions ======================
#############################################################
def ltos(l):
    s = ""
    for c in l:
        s+= c + ", "
    return s[:-2]

def isSubseq(x, y):
    it = iter(y)
    return all(any(c == ch for c in it) for ch in x)

def saveConfig():
    return 0

#############################################################
#======================= Timer Class ========================
#############################################################
class Timer(Thread):
    global g_bIsDoneGame
    global g_bDebugMode
    def __init__(self,val):
        Thread.__init__(self)
        self.val = val
        self.nTime = 120000
        self.bTimerUp = False
    def run(self):
        if g_bDebugMode:
            print("Timer thread is starting")
        startTime = int(time.clock())*1000
        while(self.nTime > 0 and not g_bIsDoneGame):
            nTime = 120000 - (int(time.clock())*1000 - startTime)
            if nTime > 0:
                self.nTime = nTime
            else:
                self.nTime = 0
            time.sleep(1)
        self.bTimerUp = True
        if g_bDebugMode:
            print("Timer thread is ending")
        return
#############################################################
#====================== Game Functions ======================
#############################################################
def getAllWordsBtwn(mn, mx, wordList):
    return list(filter(lambda x: mn <=len(x)<= mx,wordList))

def getRandomWord(length, wordList):
    wordsLenN = list(filter(lambda x: len(x)==length,wordList))
    r = random.randint(0,len(wordsLenN)-1)
    return wordsLenN[r]

def getWordsWithLettersW(srcWord, wordList):
    lsrcWord = sorted(list(srcWord))
    newlWord = []
    for word in wordList:
        lword = sorted(list(word))
        if isSubseq(lword, lsrcWord):
            newlWord.append(word)
    return newlWord

def gameOutput():
    global g_timer
    global g_lsbGameData
    nl = False
    s = "\n"
    nLenLastWord = len(g_lsbGameData[0][0])
    for word in g_lsbGameData:
        if nLenLastWord != len(word[0]):
            s=s[:-1]+'\n\n'
            nl = False
        if not word[1]:
            s+= '-'*len(word[0])
        else:
            s+= word[0]
        
        if nl:
            s+= '\n'
            nl = False
        else:
            s+= '\t'
            nl = True
        nLenLastWord = len(word[0])
    s=s[:-1]+'\n'
    print(s)
    sMin = str((g_timer.nTime//1000)//60)
    sSec = str((g_timer.nTime//1000)%60)
    if len(sSec) == 1:
        sSec = '0'+sSec
    sTime = sMin+':'+sSec
    print(TEXT['game-promptTime']+sTime)

def game_init():
    global g_timer
    global g_lsWordsData
    global g_lsbGameData
    global g_lchGameLetters
    diffToWLen = {1:4,2:5,3:6,4:7}
    srcWord = getRandomWord(diffToWLen[int(CONFIG['difficulty'])],
                            g_lsWordsData)
    wordsUpTo = getAllWordsBtwn(3,
                                diffToWLen[int(CONFIG['difficulty'])],
                                g_lsWordsData)
    g_lsbGameData = [[word, False]
                     for word in getWordsWithLettersW(srcWord,wordsUpTo)]
    g_lchGameLetters = list(srcWord)
    random.shuffle(g_lchGameLetters)
    # Instantiates and runs timer for game
    g_timer = Timer(0)
    g_timer.setName('TimerThread')
    g_timer.start()
    ##############timerThread = threading.Thread(target=timer,name='timer')
    ##############timerThread.start()

def gameLoop():
    global g_timer
    global g_lsbGameData
    global g_lchGameLetters
    global g_bDebugMode
    isDoneRound = False
    
    # Initial output
    gameOutput()
    
    # Start Game Loop
    while (not isDoneRound):
        # 1. Check for conditions:
        #     If debug mode, display debug info.
        #     If all words are answered, round is done.
        #     If timer is up, round is done.
        if g_bDebugMode:
            print(TEXT['debug-warn'])
        if all([word[1] for word in g_lsbGameData]):
            isDoneRound = True
            return GAME_WIN
        if g_timer.bTimerUp:
            isDoneRound = True
            return GAME_LOSE
        # 2. Prompt guessable letters.
        print(TEXT['game-prompt0']+ltos(g_lchGameLetters))
        print(TEXT['game-prompt1'])
        # 3. Input from user.
        sIn = input(TEXT['util-input'])
        # 4. Process Input:
        if sIn == "xgame":
            isDoneRound = True
            print(TEXT['game-exit'])
            return GAME_QUIT
        elif sIn == " ":
            random.shuffle(g_lchGameLetters)
        elif [sIn, False] in g_lsbGameData:
            g_lsbGameData[g_lsbGameData.index([sIn, False])][1] = True
        # The following input is only valid if debug mode.
        if g_bDebugMode:
            if sIn == 'giveMeAnswers':
                print(ltos([word[0] for word in g_lsbGameData]))
            elif sIn == 'skipToEnd':
                for word in g_lsbGameData:
                    word[1] = True
        # 5. Output
        gameOutput()
    # End Game Loop
    
#############################################################
#====================== App  Functions ======================
#############################################################
def app_init():
    global g_lsWordsData
    global TEXT
    global CONFIG
    # Notify user app is initiating.
    print("initiating app...")
    # Parse words from WORDS_FILE for use as list of possible words
    # in game. Only use store words less than 7 char long.
    with open(WORDS_FILE, 'r') as wordFile:
        for line in wordFile:
            if len(line.strip()) <= 7:
                g_lsWordsData.append(line.strip())
    # Sort words by 1. asc length -> 2. asc value.
    g_lsWordsData = sorted(g_lsWordsData)
    g_lsWordsData = sorted(g_lsWordsData, key=lambda x: len(x))
    # Parse data from xml DATA_FILE for strings used in the app.
    dataTree = ET.parse(DATA_FILE)
    for dataChild in dataTree.getroot():
        if dataChild.tag == 'strings':
            for string in dataChild:
                if string.tag == 'text':
                    TEXT[string.attrib['id']] = string.text
    # Parse data from xml CONFIG_FILE for configuration settings.
    configTree = ET.parse(CONFIG_FILE)
    for configChild in configTree.getroot():
        if configChild.tag == 'difficulty':
            CONFIG['difficulty'] = configChild.attrib['value']
    # Notify user app is ready.
    print(TEXT['app-initDone'])
    print(TEXT['app-welcome']+'\n')
    print(TEXT['lcs-cond'])

# Shows controls
def controls():
    print(TEXT['err-nyi'])
    return 0

# Shows editable settings
def settings():
    print(TEXT['err-nyi'])
    # print('Difficulty: ', CONFIG['difficulty'])
    # newDifficulty = input(TEXT['util-input'])
    # saveConfig()
    return 0

# Shows credits and licensing info
def credits_():
    print(TEXT['lcs-credits'])
    return 0

# Game main function   
def game():
    global g_bIsDoneGame
    g_bIsDoneGame = False
    while(not g_bIsDoneGame):
        # Inits game
        game_init()
        # Runs game loop
        n = gameLoop()
        g_timer.join()
        # Processes exit conditions
        if n == GAME_QUIT:
            g_bIsDoneGame = True
        elif n == GAME_WIN:
            print(TEXT['game-win'])
            print(TEXT['game-prompt2'])
            sIn = input(">>> ")
            while (sIn not in 'YyNn'):
                print(TEXT['err-in'])
                print(TEXT['game-prompt2'])
                sIn = input(TEXT['util-input'])
            if sIn in 'Nn':
                g_bIsDoneGame = True
        elif n == GAME_LOSE:
            print(TEXT['game-lose'])
            print(TEXT['game-answers'])
            print(ltos([word[0] for word in g_lsbGameData]))
            print(TEXT['game-prompt2'])
            sIn = input(">>> ")
            while (sIn not in 'YyNn'):
                print(TEXT['err-in'])
                print(TEXT['game-prompt2'])
                sIn = input(TEXT['util-input'])
            if sIn in 'Nn':
                g_bIsDoneGame = True
        else:
            print(TEXT['err-gameHalt'])
        
        
#############################################################
#======================== Main Loop =========================
#############################################################
if __name__=='__main__':
    
    app_init()

    while (not g_bIsDone):    
        print('')
        print(TEXT['app-titleBorder'])
        print(TEXT['app-title'])
        print(TEXT['app-titleBorder'])
        print('')
        # If debug mode, display debug info.
        if g_bDebugMode:
            print(TEXT['debug-warn'])
        print(TEXT['app-menu1'])
        print(TEXT['app-menu2'])
        sIn = input(TEXT['util-input'])
        # Menu to app functions
        if sIn in 'Pp':
            game()
        elif sIn in 'Xx':
            g_bIsDone = True
        elif sIn in 'Cc':
            controls()
        elif sIn in 'Ss':
            settings()
        elif sIn in 'Rr':
            credits_()
    #   v------- START DEBUG COMMANDS -------v
        elif sIn in 'Dd':
            g_bDebugMode = not g_bDebugMode
    #   ^-------- END DEBUG COMMANDS --------^
        else:
            print(TEXT['err-noSuchCommand'])

    # Prints notif when app is done
    print(TEXT['app-done'])
