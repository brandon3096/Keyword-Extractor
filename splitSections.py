import sys
from sys import argv


#Input: Document string
#Output: Abstract, Conclusion, All Else (in that order)
#expected fname: "SemEval2010/test/C-1.txt.final"
def splitSections(fname):
    with open(fname) as f:
        lower_case = False
        str = f.read()
        str.rstrip('\n')
        
        #Split Abstract from rest of document
        #Some documents use lower case, some upper case, account for both
        #Set of Words from Abstract -> Introduction
        try:
            abstract_extended = str.split('ABSTRACT')[1]
        except IndexError:
            abstract_extended = str.split('Abstract')[1]
            lower_case = True

        if lower_case:
            abstract = abstract_extended.split('Introduction')[0]
        else:
            abstract = abstract_extended.split('INTRODUCTION')[0]
        #print abstract

        #Split Conclusion from rest of document
        #Conclusion -> References
        if lower_case:
            conclusion_ext = str.split('Conclusion')[1]
            conclusion = conclusion_ext.split('Reference')[0]
        else:
            conclusion_ext = str.split('CONCLUSION')[1]
            conclusion = conclusion_ext.split('REFERENCE')[0]

        #print conclusion


        #Everything else
        if lower_case:
            body = str.split('Abstract')[1]
            body = body.split('Conclusion')[0]
        else:
            body = str.split('ABSTRACT')[1]
            body = body.split('CONCLUSION')[0]

        #print body
        return abstract, conclusion, body

#Testing
doc = argv[1]
splitSections(doc)
