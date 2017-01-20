#READ: intended to run as 'python printToExcel.py 'C-22.txt.final''
#Will return you with tokenized versions of the answer key for specified test file
#Inside, appropriate functions will calculate precision and recall given the aforementioned token list and the keywords that we have retrieved
#Then, a printToExcel function exists to write individual p+r scores as they are calculated iteratively

from sys import argv
import xlwt
import preprocess

#Expected test_file_name to be in the form of "C-1.txt.final..."
#Function will return a list of tokenized keywords chosen as solution words
def preprocessSolution(test_file_name):
    #open answer key
    fname = 'SemEval2010/test_answer/test.reader.stem.final'
    
    #determine which file we want, first four letters are unique identifiers
    doc_id = test_file_name[0] + test_file_name[1] + test_file_name[2]
    if test_file_name[3] == '.':
        doc_id += ' '
    else:
        doc_id += test_file_name[3]

    tokens = ""
    counter = 0
    
    with open(fname) as f:
        for line in f:
            doc_id_compare = line[0] + line[1] + line[2] + line[3]
            if doc_id_compare == doc_id:
                tokens = line
                break
            counter += 1
            
    tokens = preprocess.tokenizeText(tokens)
    tokens = preprocess.removeStopwords(tokens)
    tokens = preprocess.stemWords(tokens)
    return tokens

#Precision: the fraction of retrieved keywords that appear in the test solution  
#Precision = (#Relevant Keywords Extracted) / (Total # Keywords Retrieved)       
#Input: List of solution keywords and list of retrieved keywords
#Output: float (fraction)
def calculatePrecision(solution_list, retrieved_list):

    correct = 0
    total = 0
    
    #compare all entries in retrieved list against solution list
    for r in retrieved_list:
        found = False
        for s in solution_list:
            if r == s:
                correct += 1
#                print r
                found = True
                break
        total += 1
    
    precision = float(correct) / float(total)
    return precision

#Input: List of solution keywords and list of retrieved keywords
#Output: float (fraction)
#Recall: fraction of relevant instances that are retrieved
#Recall = (#Relevant Keywords Extracted) / (Total # Keywords in Solution) 
def calculateRecall(solution_list, retrieved_list):
    solution_size = len(solution_list)
    correct = 0

    #compare all entries in retrieved list against solution list
    for r in retrieved_list:
        found = False
        for s in solution_list:
            if r == s:
                correct += 1
#                print r
                found = True
                break

    recall = float(correct) / float(solution_size)
    return recall
                
#Function will write precision + recall statistics to already opened Excel book
#'counter' is used in anticipation of a loop
def printToExcel(precision, recall, doc, counter, ws):
        ws.write(counter, 0, precision)
        ws.write(counter, 1, recall)
        ws.write(counter, 2, doc)
    
if __name__ == "__main__":
#Expected doc_name to be in the form of "X-1..."
    doc_name = argv[1]

    solution_tokens = preprocessSolution(doc_name) 
    print solution_tokens

    #Example of a list of retrieved keywords
    retrieved_example = ['data', 'mobil object framework', 'java', 'metric collect', 'junk', 'random', 'measur', 'framework']
    precision = calculatePrecision(solution_tokens, retrieved_example)
    print precision 
    recall = calculateRecall(solution_tokens, retrieved_example)
    print recall

    #Write to excel
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Precision and Recall')
    printToExcel(precision, recall, 0, ws) 
    wb.save('498_Results.csv')
