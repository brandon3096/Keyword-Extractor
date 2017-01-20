#Brandon Oyer, Andrew Giugliano, Haemini Park, Nick Pangori -- Final EECS498 Project

#first arg on command line is weighting scheme (tfidf, nfxbpx, etc.), second is directory of files

import os
import sys
import math
import xlwt
import operator
import porter_stemmer
import preprocess
import printToExcel
import splitSections

def tokenize(doc):

    tokens = preprocess.tokenizeText(doc)
    tokens = preprocess.removeStopwords(tokens)
    tokens = preprocess.stemWords(tokens)

    return tokens

def indexDocument(doc_number, document, inv_index):

    #preprocess
    tokens = tokenize(document)

    frequencies = {}
    frequencies = preprocess.doStats(tokens, frequencies)

    #indexing (in: tokens, out: updated inverted index)
    for x in frequencies:
        if(x in inv_index):
            #increase df
            inv_index[x][0] += 1
            #update document:frequency map for term x
            inv_index[x][1][doc_number] = frequencies[x]
        
        else:
            #list to hold df and a document:frequency map for term x
            inv_index[x] = []
            inv_index[x].append(1)
            doc_termfreq_map = {}
            doc_termfreq_map[doc_number] = frequencies[x]
            inv_index[x].append(doc_termfreq_map)

    return inv_index, frequencies

def weightDocs(dv_lengths_f, dv_weights_f, inv_index, scheme, coefficient1, coefficient2, coefficient3):
    
    dv_lengths = {}
    for y in dv_lengths_f:
        #make abstract/conclusion/body token lists
        abstract, conclusion, body = splitSections.splitSections("SemEval2010/test/"+y)

        abstractTokens = tokenize(abstract)
        bodyTokens = tokenize(body)
        conclusionTokens = tokenize(conclusion)

        length = 0
        dv_weights = {}
        
        if(scheme == 'tfidf'):
            #for each token in the document
            for x in dv_lengths_f[y]:
                tokenWeight = ((float(inv_index[x][1][y]))*float(math.log10(float(doc_counter)/float(inv_index[x][0]))))
                #Apply extra weighting for abstract, body, conclusion
                if x in abstractTokens:
                    tokenWeight *= float(coefficient1)
                if x in bodyTokens:
                    tokenWeight *= float(coefficient2)
                if x in conclusionTokens:
                    tokenWeight *= float(coefficient3)
                length += float(tokenWeight**2)
                dv_weights[x] = tokenWeight
    
        elif(scheme == 'txctxx'):
            for x in dv_lengths_f[y]:
                tokenWeight = float(inv_index[x][1][y])
                if x in abstractTokens:
                    tokenWeight *= float(coefficient1)
                if x in bodyTokens:
                    tokenWeight *= float(coefficient2)
                if x in conclusionTokens:
                    tokenWeight *= float(coefficient3)
                length += float(tokenWeight**2)
                dv_weights[x] = tokenWeight

        elif(scheme == 'nxxbpx'):
            for x in dv_lengths_f[y]:
                tokenWeight = float(.5)+((float(.5)*float(inv_index[x][1][y]))/float(max(dv_lengths_f[y].iteritems(), key=operator.itemgetter(1))[1]))
                if x in abstractTokens:
                    tokenWeight *= float(coefficient1)
                if x in bodyTokens:
                    tokenWeight *= float(coefficient2)
                if x in conclusionTokens:
                    tokenWeight *= float(coefficient3)
                length += float(tokenWeight**2)
                dv_weights[x] = tokenWeight

        elif(scheme == 'idf'):
            for x in dv_lengths_f[y]:
                tokenWeight = float(math.log10(float(doc_counter)/float(inv_index[x][0])))
                if x in abstractTokens:
                    tokenWeight *= float(coefficient1)
                if x in bodyTokens:
                    tokenWeight *= float(coefficient2)
                if x in conclusionTokens:
                    tokenWeight *= float(coefficient3)
                length += float(tokenWeight**2)
                dv_weights[x] = tokenWeight

        elif(scheme == 'bxxbpx'):
            for x in dv_lengths_f[y]:
                tokenWeight = float(1)
                if x in abstractTokens:
                    tokenWeight *= float(coefficient1)
                if x in bodyTokens:
                    tokenWeight *= float(coefficient2)
                if x in conclusionTokens:
                    tokenWeight *= float(coefficient3)
                length += float(tokenWeight**2)
                dv_weights[x] = tokenWeight

        length = float(math.sqrt(float(length)))
        dv_lengths[y] = length
        dv_weights_f[y] = dv_weights

        sortedAnswer = sorted(dv_weights_f[y].items(), key=operator.itemgetter(1), reverse=True)

    return dv_lengths, dv_weights_f

def writeToExcel(answers, scheme, coefficient1, coefficient2, coefficient3):
    
    #Make workbook and sheet
    x = 0
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Precision and Recall')
    
    #Write to sheet with rows as [Precision][Recall][Filename] format
    for testFile in answers:
        answerTokens = printToExcel.preprocessSolution(testFile)
        precision = printToExcel.calculatePrecision(answerTokens, answers[testFile])
        recall = printToExcel.calculateRecall(answerTokens, answers[testFile])
        printToExcel.printToExcel(precision, recall, testFile, x, ws)
        x += 1
    
    wb.save('498_Results_'+scheme+'_'+coefficient1+'_'+coefficient2+'_'+coefficient3+'.csv')

#command line args
scheme      = sys.argv[1]
dir         = sys.argv[2]

#extra weighting given to the abstract
coefficient1 = sys.argv[3]
#extra weighting given to the body
coefficient2 = sys.argv[4]
#extra weighting given to the conclusion
coefficient3 = sys.argv[5]

inv_index = {}
frequencies = {}

#map [doc_number:map of token frequencies]
dv_lengths_f = {}
#map [doc_number:map of token weights]
dv_weights_f = {}

#build inverted index
doc_counter = 0
for f in os.listdir(dir):
    #get doc number
    doc_number = str(f)
    if('.txt' not in doc_number):
        continue
    
    #proceed to fill data structures with document info
    file = open(dir+f)
    input = file.read()
    inv_index, frequencies = indexDocument(doc_number, input, inv_index)
    dv_lengths_f[doc_number] = frequencies
    doc_counter += 1

#make document lengths and token weights
dv_lengths, dv_weights_f = weightDocs(dv_lengths_f, dv_weights_f, inv_index, scheme, coefficient1, coefficient2, coefficient3)

#sort weights of tokens for each doc, output top 10 words
retrievedTokens = {}
for n in dv_weights_f:
    retrievedTokens[n] = []
    sortedAnswer = sorted(dv_weights_f[n].items(), key=operator.itemgetter(1), reverse=True)
    
    for x in range(0,10):
        retrievedTokens[n].append(sortedAnswer[x][0])

writeToExcel(retrievedTokens, scheme, coefficient1, coefficient2, coefficient3)
