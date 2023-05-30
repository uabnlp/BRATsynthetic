from distribution_metrics import counters_to_jensenshannon
from math import log2
import pylcs

import pathlib
import glob
import collections
from collections import defaultdict
from collections import Counter

from tqdm import tqdm

import spacy
#import scispacy
import medspacy
from medspacy.ner import TargetRule
#from medspacy.context import ConTextComponent
#from cycontext import ConTextItem, ConTextComponent
import negspacy
from negspacy.negation import Negex

from spacy.training import Alignment


## INPUT PARAMETERS
#model_name = "en_ner_bc5cdr_md"
model_name="en_core_sci_sm"
show_file_stats = True
compute_alignment = False


print("Using "+model_name)
modelnlp = spacy.load("en_core_sci_sm") 
print(modelnlp.pipe_names)


# Span MedSpacy context works with spans only
# Snippet taken from https://github.com/medspacy/medspacy/blob/master/notebooks/14-Span-Groups.ipyn
target_rules = [
    TargetRule(literal="abdominal pain", category="PROBLEM"),
    TargetRule("recurrent use in situations in which it is physically hazardous'", "RISKY_USE"),
    TargetRule("suboxone clinic", "TREATMENT"),
    TargetRule("methadone clinic", "TREATMENT"),
    TargetRule("intoxication", "RISKY_USE"),
    TargetRule("craving", "PROBLEM"),
    TargetRule("opiate dependence", "PHARMALOGICAL_PROBLEMS"),
    TargetRule("opioid dependence", "PHARMALOGICAL_PROBLEMS"),
    TargetRule("addiction", "LOSS_OF_CONTROL"),
    TargetRule("overdose", "OVERDOSE"),
    TargetRule("opioid use", "OPIATE_USE"),
    TargetRule("opiate use", "OPIATE_USE"),
    TargetRule("opioid abuse", "OPIATE_USE"),
    TargetRule("opiate abuse", "OPIATE_USE"),
    TargetRule("heroin abuse", "OPIATE_USE"),
    TargetRule("heroin use", "OPIATE_USE"),
    TargetRule("use heroin", "OPIATE_USE"),
    TargetRule("homeless", "SOCIAL_PROBLEMS"),
    TargetRule("violence", "SOCIAL_PROBLEMS"),
    TargetRule("withdrawal", "WITHDRAWL"),
    TargetRule("opioid use disorder", "OUD"),
    TargetRule("opiate use disorder", "OUD"),
    TargetRule("OUD", "OUD"),
    TargetRule("relapse", "RELAPSE"),
    TargetRule("Alzheimers", "PROBLEM"),
    TargetRule("Parkinsons", "PROBLEM"),
    TargetRule("asthma", "PROBLEM"),
    TargetRule("COPD", "PROBLEM"),
]
nlp = spacy.blank("en")
nlp.add_pipe("medspacy_pyrush") # Not sure what this does
matcher = nlp.add_pipe("medspacy_target_matcher", config={"result_type":"group"})
matcher.add(target_rules)
context = nlp.add_pipe("medspacy_context", config={"input_span_type": "group"})
print("Rule-based OUD Model")
print(nlp.pipe_names)

#root = pathlib.Path("/data/user/ozborn/OUD/oud_2_6_2/synthetic")
root = pathlib.Path("./test")
print("Looking at files in " + str(root))


# Global Hash, 
# hash1 key=file name (a.txt), value=hash2
# hash2 key=BRAT type(ex. markov), value=hash3
# hash3 key=data_hash|compare_hash
# data_hash key=task (token_list), value=lists of data
# compare_hash key=file_name (b.txt), value=hash_c1
# hash_c1 key=task (token_list), value=comparison_result (ex 0.87)

brat_types = ['consist', 'random', 'markov', 'simple', 'orig']
all_tasks = {'dep_list':'Dependency', 'token_list':'Tokens', 'ent_list':'Entities', 'pos_list':'PartOfSpeech', 'span_list':'Spans'}
all_counts = {'neg_count':'Negs','family_count':'Family','historical_count':'Hist','tok_count':'Tokens','span_count':'Spans'}
allResults = {}
#overallResults = dict.fromkeys(brat_types, dict.fromkeys(all_counts.keys(),0))
overallResults = defaultdict(dict)
overallResults.update((k, {}) for k in brat_types)
for empty in overallResults.values():
    for task in all_counts.keys():
        empty[task]=0

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


def get_alignment(A,B):
    res = pylcs.lcs_string_idx(A, B)
    return res


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
def getData(doc,data):
    token_list = [token.text for token in doc]
    span_list = [span.text for span in doc.spans["medspacy_spans"]]
    data['span_list'] = Counter(span_list)
    data['token_list'] = Counter(token_list)

    data['neg_count'] = sum(map(lambda x: 1 if x._.is_negated else 0, doc.spans["medspacy_spans"]))
    data['family_count'] = sum(map(lambda x: 1 if x._.is_family else 0, doc.spans["medspacy_spans"]))
    data['historical_count'] = sum(map(lambda x: 1 if x._.is_historical else 0, doc.spans["medspacy_spans"]))
    data['tok_count'] = sum(map(lambda x: 1, token_list))
    data['span_count'] = sum(map(lambda x: 1, span_list))
    return data


def add_model_data(data,doc):
    ecount = sum(map(lambda x: 1, doc.ents))
    pos_list = [token.pos_ for token in doc]
    dep_list = [token.dep_ for token in doc]
    ent_list = [ent.text for ent in doc.ents]
    data['pos_list'] = Counter(pos_list)
    data['dep_list'] = Counter(dep_list)
    data['ent_list'] = Counter(ent_list)
    data['entity_count'] = ecount
    #print(data['ent_list'])



def getDocString(f):
    text_file = open(f, "r")
    data = text_file.read()
    text_file.close()
    return data


def fetchCount(bratver, fname, task):
    taskresult = allResults[fname][bratver]['data'][task]
    return ("\t" + str(taskresult), taskresult)


def print_context_counts(d):
    out = 'Raw Global Context Counts\n'
    result_order = d['orig'].keys()
    for task in result_order:
        abbrev = all_counts[task]
        out += "\t"+abbrev
    for brat,task_results in d.items():
        output = str(brat)
        for count_type,results in task_results.items():
            output = output+"\t"+str(results)
        out+="\n"+output
    print("\n"+out)


def print_file_context_counts():
    for filecount,fname in tqdm(enumerate(allResults.keys()),desc='Computing File Stats'):
        out = ''
        for count_type,abbrev in all_counts.items():
            out += "\t"+abbrev
        for t in brat_types:
            output = str(t)
            for count_type,abbrev in all_counts.items():
                output = output + fetchCount(t, fname, count_type)[0]
            out+="\n"+output
        print("\n"+out)


def compute_file_statistics():
    task_scores = dict.fromkeys(all_tasks.keys(), {})
    for task in task_scores.keys():
        task_scores[task] = dict.fromkeys(brat_types, 0.0)

    for filecount,fname in tqdm(enumerate(allResults.keys()),desc='Computing File Stats'):
        # File Stats
        task_scores['dep_list'] = compute_stats(fname, 'dep_list',task_scores['dep_list'])
        task_scores['span_list'] = compute_stats(fname, 'span_list',task_scores['span_list'])
        task_scores['token_list'] = compute_stats(fname, 'token_list',task_scores['token_list'])
        task_scores['pos_list'] = compute_stats(fname, 'pos_list',task_scores['pos_list'])
        #total_dep_scores = compute_stats(fname, 'dep_list', total_dep_scores)
    return task_scores


# For input filename and task, compute stats versus the original
def compute_stats(fname, task, old_scores):
    task_data_to_compare = []
    ref = Counter(allResults[fname]['orig']['data'][task])
    ref_string = allResults[fname]['orig']['doc_text']
    task_data_to_compare.append(ref)
    # print("Original Counter:"+str(ref))
    result_scores = dict.fromkeys(brat_types, 0)
    for t in brat_types:
        c = Counter(allResults[fname][t]['data'][task])
        task_data_to_compare.append(c)
        #j = calculate_jacard(task_data_to_compare)
        jen = counters_to_jensenshannon(task_data_to_compare[0],task_data_to_compare[1])
        if(compute_alignment is True):
            compare_string = allResults[fname][t]['doc_text']
            align = get_alignment(ref_string,compare_string)
            align_count = sum(map(lambda s: s!=-1, align))
        task_data_to_compare.pop()
        # Running total of file summary stats for all BRATsynthetic types
        result_scores[t] = old_scores[t] + jen
    return result_scores


def print_overall_average_statistics(all_task_scores):

    total_files = len(allResults.keys())
    # Overall stats for all files
    print("\nFile Jensen-Shannon Overall Stats")

    # Sum and Normalize scores
    total_result_scores = dict.fromkeys(all_tasks.keys(), {})
    for task in total_result_scores.keys():
    	total_result_scores[task] = {k:v/total_files for (k,v) in all_task_scores[task].items()}

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
            task_row_output[task] += "\t"+f'{total_result_scores[task][j]:.3f}'
        print(task_row_output[task])
    print(str(total_files)+" files examined")


# Get distribution of all POS tags, dependencies, etc...
def get_overall_distributions(overall):
    for filecount,fname in tqdm(enumerate(allResults.keys()),desc='Summing Counts into Distributions'):
        for t in brat_types:
            for tally in all_counts.keys():
                c = allResults[fname][t]['data'][tally]
                if(c>0):
                    updated_result = overall[t][tally] + c
                    overall[t][tally] = updated_result
            #for tally in all_distributions:
                #c = Counter(allResults[fname][t]['data'][tally])
                #overall[t][tally] = overall[t][tally] + c
    print_context_counts(overall)



def print_all_results_ids():
    for filecount,fname in tqdm(enumerate(allResults.keys()),desc='Printing All Results'):
        for t in brat_types:
            for tally in all_counts.keys():
                c = allResults[fname][t]['data'][tally]
                print(str(fname)+" "+t+" "+str(tally)+"  c value:"+str(c)+" allResults id:"+str(id(allResults[fname][t]['data'][tally])))

####### MAIN #########
#files = root.rglob("*.txt")
files = glob.iglob(str(root)+'/**/'+"*.txt",recursive=True)
for counter,f in tqdm(enumerate(files), desc='Collecting Data'):
    if(counter%10 == 0):
         print('.',end='',flush=True)
    fpath = pathlib.Path(f)
    tup = getTypeFileTupe(fpath)
    try:
        fresults = allResults[tup[1]]
    except KeyError:
        fresults = {}
        allResults[tup[1]] = fresults
    # Get results for this file
    data = getDocString(fpath)
    doc = nlp(data)
    modeldoc = modelnlp(data)

    stats = {}
    #print(str(fpath))
    stats['doc_text']=data
    count_data = dict.fromkeys(all_counts.keys(),0)
    task_data = dict.fromkeys(all_tasks.keys(),Counter())
    data = count_data | task_data
    stats['data'] = getData(doc,data)
    add_model_data(stats['data'],modeldoc)
    stats['fullpath'] = fpath
    fresults[tup[0]] = stats


if(show_file_stats is True):
    print_file_context_counts()

tscores = compute_file_statistics()
print_overall_average_statistics(tscores)
# Compute Global File-Agnostic POS Tags, Dependencies, etc... from data
overall_counts = get_overall_distributions(overallResults)

# nlp = medspacy.load(enable=["sectionizer"])
                #print(overallResults) # When consists add family value, it adds it to ALL things. May be error in allResults?
# print(nlp.pipe_names)
