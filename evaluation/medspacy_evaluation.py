from distribution_metrics import counters_to_jensenshannon
from distribution_metrics import kl_divergence
from distribution_metrics import kl_divergence_smooth
from distribution_metrics import dictionary_to_normalized_distribution
import pylcs

import pathlib
import glob
import collections
from collections import defaultdict
from collections import Counter

from tqdm import tqdm

import spacy
from spacy.training import Alignment
# import scispacy
import medspacy
from medspacy.ner import TargetRule
# from medspacy.context import ConTextComponent
# from cycontext import ConTextItem, ConTextComponent
# import negspacy
# from negspacy.negation import Negex

# INPUT PARAMETERS
# model_name = "en_ner_bc5cdr_md"
model_name = "en_core_sci_sm"
show_file_stats = True
compute_alignment = False

print("Using " + model_name)
model_nlp = spacy.load("en_core_sci_sm")
print(model_nlp.pipe_names)

# Span MedSpacy context works with spans only
# Snippet taken from https://github.com/medspacy/medspacy/blob/master/notebooks/14-Span-Groups.ipyn
oud_target_rules = [
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
nlp.add_pipe("medspacy_pyrush")  # Not sure what this does
matcher = nlp.add_pipe("medspacy_target_matcher", config={"result_type": "group"})
matcher.add(oud_target_rules)
context = nlp.add_pipe("medspacy_context", config={"input_span_type": "group"})
print("Rule-based OUD Model")
print(nlp.pipe_names)

# root = pathlib.Path("/data/user/ozborn/OUD/oud_2_6_2/synthetic")
root = pathlib.Path("./test")
print("Looking at files in " + str(root))

brat_types = ['consist', 'random', 'markov', 'simple', 'orig']
all_tasks = {'dep_list': 'Dependency', 'token_list': 'Tokens', 'ent_list': 'Entities', 'pos_list': 'PartOfSpeech',
             'span_list': 'Spans'}
all_counts = {'neg_count': 'Neg', 'family_count': 'Sub', 'historical_count': 'His', 'tok_count': 'Tok',
              'span_count': 'Spans'}
# Global Hash
allResults = {}

# Contains global results for context counts distribution in all_counts
overall_count_results = defaultdict(dict)
overall_count_results.update((k, {}) for k in brat_types)
for empty in overall_count_results.values():
    for task in all_counts.keys():
        empty[task] = 0

# Contains global results for distributions in all_tasks
overall_distribution_results = defaultdict(dict)
overall_distribution_results.update((k, {}) for k in brat_types)
for empty in overall_distribution_results.values():
    for task in all_tasks.keys():
        empty[task] = Counter()

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


def get_alignment(A, B):
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
def get_type_file_tuple(text_file):
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
def get_data(doc, data):
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


def add_model_data(data, doc):
    entity_count = sum(map(lambda x: 1, doc.ents))
    pos_list = [token.pos_ for token in doc]
    dep_list = [token.dep_ for token in doc]
    ent_list = [ent.text for ent in doc.ents]
    data['pos_list'] = Counter(pos_list)
    data['dep_list'] = Counter(dep_list)
    data['ent_list'] = Counter(ent_list)
    data['entity_count'] = entity_count


def getDocString(f):
    text_file = open(f, "r")
    data = text_file.read()
    text_file.close()
    return data


def fetchCount(bratver, fname, task):
    taskresult = allResults[fname][bratver]['data'][task]
    return "\t" + str(taskresult), taskresult


def print_context_counts(d):
    out = 'Global Context Counts\n\t'
    result_order = d['orig'].keys()
    for task_count in result_order:
        abbrev = all_counts[task_count]
        out += "\t" + abbrev
    for brat, task_results in d.items():
        output = str(brat)
        for count_type, results in task_results.items():
            output = output + "\t" + str(results)
        out += "\n" + output
    print("\n" + out)


def print_counters(d, name):
    out = 'Global Counts for ' + name + '\n\t'
    result_order = d['orig'][name].keys()
    for mini_task in result_order:
        out += "\t" + mini_task
    for synthetic_type, counter in d.items():
        output = str(synthetic_type)
        for count_type, results in counter[name].items():
            output = output + "\t" + str(results)
        out += "\n" + output
    print("\n" + out)


def print_file_context_counts():
    for filecount, fname in tqdm(enumerate(allResults.keys()), desc='Computing File Stats'):
        out = ''
        for count_type, abbrev in all_counts.items():
            out += "\t" + abbrev
        for t in brat_types:
            output = str(t)
            for count_type, abbrev in all_counts.items():
                output = output + fetchCount(t, fname, count_type)[0]
            out += "\n" + output
        print("\n" + out)


def compute_file_statistics():
    task_scores = dict.fromkeys(all_tasks.keys(), {})
    for task in task_scores.keys():
        task_scores[task] = dict.fromkeys(brat_types, 0.0)

    for filecount, fname in tqdm(enumerate(allResults.keys()), desc='Computing File Stats'):
        # File Stats
        task_scores['dep_list'] = compute_stats(fname, 'dep_list', task_scores['dep_list'])
        task_scores['span_list'] = compute_stats(fname, 'span_list', task_scores['span_list'])
        task_scores['token_list'] = compute_stats(fname, 'token_list', task_scores['token_list'])
        task_scores['pos_list'] = compute_stats(fname, 'pos_list', task_scores['pos_list'])
        # total_dep_scores = compute_stats(fname, 'dep_list', total_dep_scores)
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
        # j = calculate_jacard(task_data_to_compare)
        jen = counters_to_jensenshannon(task_data_to_compare[0], task_data_to_compare[1])
        if compute_alignment is True:
            compare_string = allResults[fname][t]['doc_text']
            align = get_alignment(ref_string, compare_string)
            align_count = sum(map(lambda s: s != -1, align))
        task_data_to_compare.pop()
        # Running total of file summary stats for all BRATsynthetic types
        result_scores[t] = old_scores[t] + jen
    return result_scores


def print_overall_average_statistics(all_task_scores):
    file_count = len(allResults.keys())
    # Overall stats for all files
    print("\nAverage File Jensen-Shannon Stats")

    # Sum and Normalize scores
    total_result_scores = dict.fromkeys(all_tasks.keys(), {})
    for task in total_result_scores.keys():
        total_result_scores[task] = {k: v / file_count for (k, v) in all_task_scores[task].items()}

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
            task_row_output[task] += "\t" + f'{total_result_scores[task][j]:.3f}'
        print(task_row_output[task])
    return file_count


# Sum integers of tokens, entities and contexts to get overall counts
def get_overall_counts(overall):
    for filecount, fname in tqdm(enumerate(allResults.keys()), desc='Summing Counts into Distributions'):
        for t in brat_types:
            for tally in all_counts.keys():
                c = allResults[fname][t]['data'][tally]
                if int(c) > 0:
                    updated_result = overall[t][tally] + c
                    overall[t][tally] = updated_result
    return overall


# Sum Counters to get distribution of all POS tags, dependencies, etc...
def get_overall_distributions(overall):
    for filecount, file_name in tqdm(enumerate(allResults.keys()), desc='Collating Distributions'):
        for syn in brat_types:
            for tally in all_tasks.keys():
                c = allResults[file_name][syn]['data'][tally]
                updated_result = overall[syn][tally] + c
                overall[syn][tally] = updated_result
    return overall


def print_all_results_ids():
    for filecount, fname in tqdm(enumerate(allResults.keys()), desc='Printing All Results'):
        for t in brat_types:
            for tally in all_counts.keys():
                c = allResults[fname][t]['data'][tally]
                print(str(fname) + " " + t + " " + str(tally) + "  c value:" + str(c) + " allResults id:" + str(
                    id(allResults[fname][t]['data'][tally])))


def print_global_kl_divergence(results_dictionary, distribution_name):
    print("\nKL Divergence for Global " + distribution_name)
    for synthetic_type in brat_types:
        if synthetic_type == "orig":
            continue
        synthetic_distribution = dictionary_to_normalized_distribution(results_dictionary, synthetic_type, "orig",
                                                                       ([], []))
        print(
            synthetic_type + "\t" + f'{(kl_divergence_smooth(synthetic_distribution[0], synthetic_distribution[1])):.3f}')


def make_results_dictionary_for_distribution(distribution_results, distribution_type):
    some_results = defaultdict(dict)
    some_results.update((k, {}) for k in brat_types)
    for some_synthetic_type, some_task in distribution_results.items():
        some_results[some_synthetic_type] = distribution_results[some_synthetic_type][distribution_type]
    return some_results


####### MAIN #########
# files = root.rglob("*.txt")
files = glob.iglob(str(root) + '/**/' + "*.txt", recursive=True)
for counter, f in tqdm(enumerate(files), desc='Collecting Data'):
    if counter % 10 == 0:
        print('.', end='', flush=True)
    fpath = pathlib.Path(f)
    tup = get_type_file_tuple(fpath)
    try:
        file_results = allResults[tup[1]]
    except KeyError:
        file_results = {}
        allResults[tup[1]] = file_results
    # Get results for this file
    data = getDocString(fpath)
    doc = nlp(data)
    model_doc = model_nlp(data)

    stats = {'doc_text': data}
    # print(str(fpath))
    count_data = dict.fromkeys(all_counts.keys(), 0)
    task_data = dict.fromkeys(all_tasks.keys(), Counter())
    data = count_data | task_data
    stats['data'] = get_data(doc, data)
    add_model_data(stats['data'], model_doc)
    stats['fullpath'] = fpath
    file_results[tup[0]] = stats

if show_file_stats is True:
    print_file_context_counts()

total_files = print_overall_average_statistics(compute_file_statistics())
print(str(total_files) + " files examined, end of files stats")

# Compute Global File-Agnostic from Counts
overall_counts = get_overall_counts(overall_count_results)
print_context_counts(overall_counts)
print_global_kl_divergence(overall_counts, "context counts")

# Compute Global File-Agnostic from tasks like POS Tags, Dependencies, etc..
overall_distributions = get_overall_distributions(overall_distribution_results)
for some_task in all_tasks.keys():
    print_counters(overall_distributions, some_task)
    print_global_kl_divergence(make_results_dictionary_for_distribution(overall_distributions, some_task), some_task)
