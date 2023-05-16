import spacy
import scispacy
import medspacy
import pathlib
from spacy.training import Alignment
from itertools import tee
from collections import Counter

model_name="en_ner_bc5cdr_md"
#model_name="en_core_sci_sm"
nlp = spacy.load(model_name)
print("Loaded model "+model_name)

root = pathlib.Path("/data/user/ozborn/OUD/test")
#root = pathlib.Path("/data/user/ozborn/OUD/oud_2_6/deidentification")
#root = pathlib.Path("/data/user/ozborn/OUD/oud_2_6/deidentification/deidentification_synthetic_random/dev")
print("Looking at files in "+str(root))

# Global Hash, 
# hash1 key=file name (a.txt), value=hash2
# hash2 key=BRAT type(ex. markov), value=hash3
# hash3 key=data_hash|compare_hash
# data_hash key=task (token_list), value=lists of data
# compare_hash key=file_name (b.txt), value=hash_c1
# hash_c1 key=task (token_list), value=comparison_result (ex 0.87)
brat_types = ['consistent','random','markov']
tests = { 'Identical Token Count':'token_list', 'Identical POS Token Count':'pos_list', 'Identical Dependency Count':'dep_list', 'Entity Count':'ent_list'}
#allResults = dict.fromkeys(keys, {})
allResults = {}
print("Initialization complete, getting data....")

# Function aligns tokens between 2 documents in order to compare attributes
# https://spacy.io/usage/linguistic-features#aligning-tokenization
def align_tokens(doc1,doc2):
   n1 = nlp(doc1)
   n2 = nlp(doc2)
   tokens1  = [i.text for i in n1]
   tokens2  = [i.text for i in n2]
   align = Alignment.from_strings(tokens1, tokens2)
   print(f"a -> b, lengths: {align.x2y.lengths}")  # array([1, 1, 1, 1, 1, 1, 1, 1])
   print(f"a -> b, mapping: {align.x2y.data}")  # array([0, 1, 2, 3, 4, 4, 5, 6]) : two tokens both refer to "'s"
   print(f"b -> a, lengths: {align.y2x.lengths}")  # array([1, 1, 1, 1, 2, 1, 1])   : the token "'s" refers to two tokens
   print(f"b -> a, mappings: {align.y2x.data}")  # array([0, 1, 2, 3, 4, 5, 6, 7])
   #Count non 1 to 1 mappings, Sum of 1 to 1 mappings for both / 2 - later average it
   n1perfects=sum(map(lambda x: 1 if x == 1 else 0, align.x2y.data))
   n2perfects=sum(map(lambda x: 1 if x == 1 else 0, align.y2x.data))
   return (n1perfects+n2perfects)/2

# Returns BRATsynthetic processing type,file name
def getTypeFileTupe(text_file):
   path_parts = list(text_file.parts)
   fname = path_parts[len(path_parts)-1]
   #brat_type = path_parts[len(path_parts)-2]
   #print(str(path_parts))
   brat_type=None
   if any("random" in word for word in path_parts):
      brat_type='random'
   elif any("markov" in word for word in path_parts):
      brat_type='markov'
   elif any("consistent" in word for word in path_parts):
      brat_type='consistent'
   else:
      print("Error:"+str(path_parts))
   #print(brat_type)
   #print(fname)
   return brat_type,fname


# Get total entity count, entity_count, modifier_counts
def getData(doc):
   token_list = [token.text for token in doc]
   #print(token_list)
   #pos_list = [token.pos_ for token in doc]
   dep_list = [token.dep_ for token in doc]
   ent_list = [ent.text for ent in doc.ents]
   data = {}
   data['token_list']=token_list
   #data['pos_list']=pos_list
   data['dep_list']=dep_list
   data['ent_list']=ent_list
   #for ent in doc.ents:
   #    if(ent._.is_negated):
   #       print("Found negated!")
   #   print(ent, ent._.is_negated, ent._.is_family, ent._.is_historical)

   ecount=sum(map(lambda x: 1, doc.ents))
   negcount=sum(map(lambda x: 1 if x._.is_negated else 0, doc.ents))
   fcount=sum(map(lambda x: 1 if x._.is_family else 0, doc.ents))
   hcount=sum(map(lambda x: 1 if x._.is_historical else 0, doc.ents))
   tokcount=sum(map(lambda x: 1, token_list))
   data['entity_count']=ecount
   data['neg_count']=negcount
   data['family_count']=fcount
   data['historical_count']=hcount
   data['tok_count']=tokcount
   counts = (ecount,negcount,fcount,hcount)
   return data

def getDocString(f):
   text_file = open(f, "r")
   data = text_file.read()
   text_file.close()
   return data

# FIX, should iterate through all files, then  rglob
#def analyzeData():
#   fiter = allResults[bratver].keys()
#   first_it,second_it = tee(fiter)
#   for bratver in allResults.keys():
#      print("Comparing "+bratver)
#      for file1 in first_it:
#         for file2 in second_it:
#            fullpath1 = allResults[bratver][file1]['fullpath']
#            fullpath2 = allResults[bratver][file2]['fullpath']
#            if(fullpath1==fullpath2):
#               print("same file, no compare:"+str(fullpath1)+" to "+str(fullpath2))
#            else:
#               if(file1!=file2):
#                  print("different files:"+file1+" and "+file2)
#                  continue
#               d1 = getDocString(fullpath1)
#               d2 = getDocString(fullpath2)
#               token_sim = align_tokens(d1,d2)
#               print("Comparing "+str(file1)+str(token_sim))


def fetchCount(bratver,fname,task):
   taskresult = allResults[fname][bratver]['data'][task]
   return ("\t"+str(taskresult),taskresult)


def appendCount(bratver,fname):
   output= str(bratver)
   if(bratver in ['markov','random']):
      output = output+"   "
   output = output+fetchCount(bratver,fname,"entity_count")[0]
   output = output+fetchCount(bratver,fname,"neg_count")[0]
   output = output+fetchCount(bratver,fname,"tok_count")[0]
   output = output+fetchCount(bratver,fname,"family_count")[0]
   output = output+fetchCount(bratver,fname,"historical_count")[0]
   return output


def printCounts():
   print("\t\tEnts\tNegs\tTokens\tFamily\tHist")
   for fname in allResults.keys():
      print(fname)
      print(appendCount("markov",fname))
      print(appendCount("random",fname))
      print(appendCount("consistent",fname))
      



####### MAIN #########
# Which you can wrap in a list() constructor to materialize
#list(root.iterdir())
files = root.rglob("*.txt")
for f in files:
   tup = getTypeFileTupe(f)
   try:
      fresults = allResults[tup[1]]
   except KeyError:
      fresults = {}
      allResults[tup[1]] = fresults
   # Get results for this file
   data = getDocString(f)
   doc = nlp(data)

   stats = {}
   stats['data'] = getData(doc)
   stats['fullpath']=f
   #try:
   #   results = fresults[tup[0]]
   #except KeyError:
   #   results={}
   fresults[tup[0]]=stats


printCounts()

#nlp = medspacy.load(enable=["sectionizer"])
#print(nlp.pipe_names)
