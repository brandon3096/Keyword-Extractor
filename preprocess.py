#Brandon Oyer, Andrew Giugliano, Nick Pangori, Haemini Park -- Final EECS498 Project

import re
import os
import sys
import operator
import porter_stemmer


def removeSGML(string):

    i = 0

    while i in range(0,len(string)):
        if(string[i] == '<'):
            marker = 1
            for j in range(i+1, len(string)):
                if(string[j] == '<'):
                    marker = marker + 1
                elif(string[j] == '>'):
                    if(marker == 1):
                        string = string[:i] + string[j+1:]
                        i = -1
                        break
                    marker = marker - 1
        i = i + 1

    return string

def tokenizeText(string):

    tokens = []

    #catch all complete (day and month and year) dates first, tokenize, remove from input string
    #d/m/y and m/d/y formats, optional comma after second word, optional period for abbreviated months
    p = re.compile(r"""
        (((0[1-9])|(1[0-9])|(2[0-9])|(3[0-1])|([1-9]))[ ]                       #day
        (Jan[.]{0,1}|January|Feb[.]{0,1}|February|March|April|May|June|July|    #month
        Aug[.]{0,1}|August|Sept[.]{0,1}|September|Oct[.]{0,1}|October|
        Nov[.]{0,1}|November|Dec[.]{0,1}|December)[,]{0,1}[ ]
        ([0-9]{4}))                                                             #year
        |                                                                       #OR other format
        ((Jan[.]{0,1}|January|Feb[.]{0,1}|February|March|April|May|June|July|   #month
        Aug[.]{0,1}|August|Sept[.]{0,1}|September|Oct[.]{0,1}|October|
        Nov[.]{0,1}|November|Dec[.]{0,1}|December)[ ]
        ((0[1-9])|(1[0-9])|(2[0-9])|(3[0-1])|([1-9]))[,]{0,1}[ ]                #day
        ([0-9]{4}))                                                             #year
        """, re.VERBOSE | re.IGNORECASE)

    #tokenize the matches to the regex
    itr = p.finditer(string)
    for m in itr:
        tokens.append(m.group())

    #remove matches from the input string so they don't get double-token'd
    string = p.sub("", string)

    #tokenize the rest of the string
    for line in string.split('\n'):
        end = len(line) - 1
        token = ""
        for j in range(0, len(line)):
            char = line[j]
            if(char.isalnum()):
                token = token + char
                if(j == end):
                    tokens.append(token)
            elif(char == ' '):
                if(len(token) != 0):
                    tokens.append(token)
                    token = ""
            elif(char == '.'):
                if(j == end):
                    #acronyms at end of line
                    if(len(line) > 2):
                        if(line[j-2] == '.'):
                            token = token + char
                    if(len(token) != 0):
                        if(len(token) == 1):                    #probably an abbreviated author first name
                            token = token + char
                        tokens.append(token)
                elif(line[j-1] == ' '):
                    #decimals
                    if(line[j+1].isdigit()):
                        token = token + char
                #acronyms
                elif(line[j+1].isalnum()):
                    token = token + char
                elif(len(token) < 5 and len(token) > 0 and line[j+1] == ' '):      #probably an abbreviation
                    token = token + char
                elif(j > 1):
                    if(line[j-2] == '.'):
                        token = token + char
            elif(char == '\''):
                if(j == end):
                    if(len(token) != 0):
                        tokens.append(token)
                #contractions
                elif(line[j+1] == 'm' and line[j-1] == 'I'):    #I'm
                    tokens.append(token)
                    token = "a"
                elif(line[j+1] == 't' and line[j-1] == 'n'):
                    if(token == 'can'):                         #can't
                        tokens.append(token)
                        token = "no"
                    elif(token == 'won'):                       #won't
                        tokens.append("will")
                        token = "no"
                    else:
                        tokens.append(token[0:len(token)-1])    #other n't contractions
                        token = "no"
                elif(line[j+1] == 'd'):
                    if(token == 'where' or token == 'how'):     #where'd / how'd
                        tokens.append(token)
                        token = "di"
                    else:                                       #other 'd contractions (assuming 'had')
                        tokens.append(token)
                        token = "ha"
                elif(line[j+1] == 's'):
                    if(token == 'let'):                         #let's
                        tokens.append(token)
                        token = "u"
                    elif(token == 'he' or token == 'how' or token == 'it' or token == 'she' or
                       token == 'somebody' or token == 'someone' or token == 'something' or token == 'that' or
                       token == 'there' or token == 'what' or token == 'when' or token == 'where' or
                       token == 'who' or token == 'why'):       #'is' contractions
                        tokens.append(token)
                        token = "i"
                    else:                                       #possessive contractions
                        tokens.append(token)
                        token = "'"
                elif(j < (end-1)):
                    if(line[j+1] == 'r' and line[j+2] == 'e'):  #'re contractions
                        tokens.append(token)
                        token = "a"
                    elif(line[j+1] == 'l' and line[j+2] == 'l'):#'ll contractions
                        tokens.append(token)
                        token = "wi"
                    elif(line[j+1] == 'v' and line[j+2] == 'e'):#'ve contractions
                        tokens.append(token)
                        token = "ha"
            elif(char == '-'):
                if(j == end):
                    if(len(token) != 0):
                        tokens.append(token)
                elif(line[j+1].isalnum() and line[j-1].isalnum()):
                    token = token + char
            elif(char == ','):
                if(j == end):
                    if(len(token) != 0):
                        tokens.append(token)
                elif(line[j+1].isdigit() and line[j-1].isdigit()):
                    token = token + char
                elif(len(token) != 0):
                        tokens.append(token)
                        token = ""
            elif(char == '/'):
                if(j == end):
                    if(len(token) != 0):
                        tokens.append(token)
                elif(line[j+1].isdigit() and line[j-1].isdigit()):
                    token = token + char

    return tokens

def removeStopwords(list):

    stop = ['a', 'all', 'an', 'and', 'any', 'are', 'as', 'at', 'be', 'been', 'but', 'by', 'few', 'from', 'for',
            'have', 'he', 'her', 'here', 'him', 'his', 'how', 'i', 'in', 'is', 'it', 'its', 'many', 'me', 'my',
            'none', 'of', 'on', 'or', 'our', 'she', 'some', 'the', 'their', 'them', 'there', 'they','that',
            'your', 'this', 'to', 'us', 'was', 'what', 'when', 'where', 'which', 'who', 'why', 'will', 'with',
            'you']

    list = [x for x in list if x not in stop]

    return list

def stemWords(list):

    stemmed = list
    stemmed_rep = []
    count = 0

    while(count == 0):
        for x in stemmed:
            y = porter_stemmer.PorterStemmer()
            stemmed_rep.append(y.stem(x, 0, len(x)-1))
        if(stemmed_rep == stemmed):
            count = 1
        else:
            stemmed = stemmed_rep
            stemmed_rep = []

    return stemmed_rep

def doStats(list, frequencyMap):

    for x in list:
        if(x in frequencyMap):
            frequencyMap[x] = frequencyMap[x] + 1
        else:
            frequencyMap[x] = 1

    return frequencyMap



#totalWords = 0
#frequencies = {}
#dir = sys.argv[1]
#for f in os.listdir(dir):
#    file = open(dir+f)
#    input = file.read()
#    output = removeSGML(input.lower())
#    tokens = tokenizeText(output)
#    tokens = removeStopwords(tokens)
#    tokens = stemWords(tokens)
#    totalWords = totalWords + len(tokens)
#    frequencies = doStats(tokens, frequencies)
#
#vocabSize = len(frequencies)
#
#print "Words %d"      %totalWords
#print "Vocabulary %d" %vocabSize
#print "Top 50 words"
#
#sortedFrequencies = sorted(frequencies.items(), key=operator.itemgetter(1), reverse=True)
#
#i = 0
#for x, y in sortedFrequencies:
#    print "%s %d" % (x, y)
#    i = i + 1
#    if(i == 50):
#        break


