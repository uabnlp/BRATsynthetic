from distribution_metrics import counters_to_jensenshannon
from math import log2
import spacy
import scispacy
import medspacy
import pathlib
import collections
from collections import Counter
from spacy.training import Alignment

model_name = "en_ner_bc5cdr_md"
# model_name="en_core_sci_sm"
nlp = spacy.load(model_name)
print("Loaded model " + model_name)

root = pathlib.Path("/data/user/ozborn/OUD/oud_2_6_2/synthetic")
root = pathlib.Path("/home/ozborn/code/repo/BRATsynthetic/evaluation/test")
# root = pathlib.Path("/data/user/ozborn/OUD/oud_2_6/deidentification/deidentification_synthetic_random/dev")
print("Looking at files in " + str(root))

# Global Hash, 
# hash1 key=file name (a.txt), value=hash2
# hash2 key=BRAT type(ex. markov), value=hash3
# hash3 key=data_hash|compare_hash
# data_hash key=task (token_list), value=lists of data
# compare_hash key=file_name (b.txt), value=hash_c1
# hash_c1 key=task (token_list), value=comparison_result (ex 0.87)

brat_types = ['consist', 'random', 'markov', 'simple', 'orig']
all_tasks = {'dep_list':'Dependency', 'token_list':'Tokens', 'ent_list':'Entities', 'pos_list':'PartOfSpeech'}
allResults = {}
print("Initialization complete, getting data....")


# Function aligns tokens between 2 documents in order to compare attributes
# https://spacy.io/usage/linguistic-features#aligning-tokenization
def align_tokens(doc1, doc2):
    n1 = nlp(doc1)
    n2 = nlp(doc2)
    tokens1 = [i.text for i in n1]
    tokens2 = [i.text for i in n2]
    align = Alignment.from_strings(tokens1, tokens2)
    print(f"a -> b, lengths: {align.x2y.lengths}")  # array([1, 1, 1, 1, 1, 1, 1, 1])
    print(f"a -> b, mapping: {align.x2y.data}")  # array([0, 1, 2, 3, 4, 4, 5, 6]) : two tokens both refer to "'s"
    print(
        f"b -> a, lengths: {align.y2x.lengths}")  # array([1, 1, 1, 1, 2, 1, 1])   : the token "'s" refers to two tokens
    print(f"b -> a, mappings: {align.y2x.data}")  # array([0, 1, 2, 3, 4, 5, 6, 7])
    # Count non 1 to 1 mappings, Sum of 1 to 1 mappings for both / 2 - later average it
    n1perfects = sum(map(lambda x: 1 if x == 1 else 0, align.x2y.data))
    n2perfects = sum(map(lambda x: 1 if x == 1 else 0, align.y2x.data))
    return (n1perfects + n2perfects) / 2



def calculate_jacard(counters):
    # for i in range(len(counters)-2):
    #   intersection = intersection & counters[i+2]

    intersection = counters[0] + counters[1]
    # intersection = Counter()
    # for c in counters:
    #   intersection &= c

    union = Counter()
    for c in counters:
        union |= c

    jacard_similarity = len(intersection) / len(union)

    # print(f"Intersection: {intersection}")
    # print(f"Union: {union}")
    # print(f"Jaccard Similarity: {jacard_similarity}")
    return jacard_similarity


# Returns BRATsynthetic processing type,file name
def getTypeFileTupe(text_file):
    path_parts = list(text_file.parts)
    fname = path_parts[len(path_parts) - 1]
    # brat_type = path_parts[len(path_parts)-2]
    # print(str(path_parts))
    brat_type = None
    if any("random" in word for word in path_parts):
        brat_type = 'random'
    elif any("markov" in word for word in path_parts):
        brat_type = 'markov'
    elif any("consist" in word for word in path_parts):
        brat_type = 'consist'
    elif any("simple" in word for word in path_parts):
        brat_type = 'simple'
    elif any("orig" in word for word in path_parts):
        brat_type = 'orig'
    else:
        print("Error:" + str(path_parts))
    # print(brat_type)
    # print(fname)
    return brat_type, fname


# Get total entity count, entity_count, modifier_counts
def getData(doc):
    data = {}
    token_list = [token.text for token in doc]
    # print(token_list)
    pos_list = [token.pos_ for token in doc]
    dep_list = [token.dep_ for token in doc]
    ent_list = [ent.text for ent in doc.ents]

    data['pos_list'] = Counter(pos_list)
    data['ent_list'] = Counter(ent_list)
    data['dep_list'] = Counter(dep_list)
    data['token_list'] = Counter(token_list)

    ecount = sum(map(lambda x: 1, doc.ents))
    negcount = sum(map(lambda x: 1 if x._.is_negated else 0, doc.ents))
    fcount = sum(map(lambda x: 1 if x._.is_family else 0, doc.ents))
    hcount = sum(map(lambda x: 1 if x._.is_historical else 0, doc.ents))
    tokcount = sum(map(lambda x: 1, token_list))
    data['entity_count'] = ecount
    data['neg_count'] = negcount
    data['family_count'] = fcount
    data['historical_count'] = hcount
    data['tok_count'] = tokcount

    return data


def getDocString(f):
    text_file = open(f, "r")
    data = text_file.read()
    text_file.close()
    return data


def fetchCount(bratver, fname, task):
    taskresult = allResults[fname][bratver]['data'][task]
    return ("\t" + str(taskresult), taskresult)


def appendCount(bratver, fname):
    output = str(bratver)
    output = output + fetchCount(bratver, fname, "entity_count")[0]
    output = output + fetchCount(bratver, fname, "neg_count")[0]
    output = output + fetchCount(bratver, fname, "tok_count")[0]
    output = output + fetchCount(bratver, fname, "family_count")[0]
    output = output + fetchCount(bratver, fname, "historical_count")[0]
    return output


def printCounts():

    total_files = 0
    total_task_scores = dict.fromkeys(all_tasks.keys(), {})
    for task in total_task_scores.keys():
        total_task_scores[task] = dict.fromkeys(brat_types, 0.0)

    print("\tEnts\tNegs\tTokens\tFamily\tHist")
    for fname in allResults.keys():
        print(fname)
        total_files += 1
        # File Stats
        for t in brat_types:
            print(appendCount(t, fname))
        total_task_scores['dep_list'] = compute_stats(fname, 'dep_list',total_task_scores['dep_list'])
        print(total_task_scores['dep_list'])
        total_task_scores['ent_list'] = compute_stats(fname, 'ent_list',total_task_scores['ent_list'])
        total_task_scores['token_list'] = compute_stats(fname, 'token_list',total_task_scores['token_list'])
        total_task_scores['pos_list'] = compute_stats(fname, 'pos_list',total_task_scores['pos_list'])
        #total_dep_scores = compute_stats(fname, 'dep_list', total_dep_scores)
        # Any file level statistics (not needed?)

    # Overall stats for all files
    print("\nOverall Stats")

    # Normalize scores
    total_result_scores = dict.fromkeys(all_tasks.keys(), {})
    for task in total_result_scores.keys():
    	total_result_scores[task] = {k:v/total_files for (k,v) in total_task_scores[task].items()}

    # Print Header
    out = "\t"
    for j in brat_types:
        out += "\t" + j
    print(out)
    # Print Data Rows
    task_row_output = dict.fromkeys(all_tasks.keys(), "")
    for task in task_row_output:
        task_row_output[task] = task
        for j in brat_types:
            task_row_output[task] += "\t"+f'{total_result_scores[task][j]:.2f}'
        print(task_row_output[task])


def compute_stats(fname, task, old_scores):
    filedeps = []
    ref = Counter(allResults[fname]['orig']['data'][task])
    filedeps.append(ref)
    # print("Original Counter:"+str(ref))
    result_scores = dict.fromkeys(brat_types, 0)
    for t in brat_types:
        c = Counter(allResults[fname][t]['data'][task])
        #print("\n"+str(fname)+":"+str(t)+" Counter:"+str(c))
        filedeps.append(c)
        #j = calculate_jacard(filedeps)
        j = counters_to_jensenshannon(filedeps[0],filedeps[1])
        filedeps.pop()
        # Running total of file summary stats for all BRATsynthetic types
        result_scores[t] = old_scores[t] + j
    return result_scores


####### MAIN #########
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
    stats['fullpath'] = f
    fresults[tup[0]] = stats

printCounts()

# nlp = medspacy.load(enable=["sectionizer"])
# print(nlp.pipe_names)
