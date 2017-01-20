# Keyword-Extractor
A Python script made for a research project that extracts keywords from research papers based on several weighting schemes

The program is run as follows:

python keywordExtractor.py [scheme (one of tfidf, txctxx, nxxbpx, idf, bxxbpx)] [path to test files (i.e. SemEval2010/test)] [abstract token weight] [body token weight] [conclusion token weight]

-The output .csv file's filename contains the scheme followed by the abstract token weight, body token weight, and conlcusion token weight. 

This is currently intended to be run on the SemEval standard academic research paper dataset, but the code is highly modular and may be modified to support other datasets, output in different formats, and perform other weighting schemes. 
