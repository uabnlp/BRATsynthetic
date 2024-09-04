import csv
from typing import Dict
from collections import Counter


def print_error_table(dhash: Dict, docid: str):
    result = docid + "\t"
    stype = ['S', 'R', 'C', 'M']
    for s in stype:
        try:
            instances = dhash[s]
            result = result + str(instances) + "\t"
        except KeyError:
            result = result + "0\t"
    print(result + "\n")


def check_subsitutions(dhash: Dict, docid: str):
    last_count = -1
    for stype, count in dhash.items():
        if last_count == -1:
            last_count = count
        else:
            if (last_count != count):
                print("Substitution type " + stype + " with count " + str(
                    count) + " does not match previous count of " + str(last_count))
                print_error_table(dhash, docid)
                return False
    return True


with open('docids.txt', newline='') as csvfile:
    result_reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    last_doc = ''
    expected_count = -1
    doc_hash = {}  # Key is subtype, value is count
    bad_docs = set()
    good_docs = set()
    for row in result_reader:
        #print(', '.join(row))
        count = row[0]
        doc = row[1].split('-')[0]
        subtype = row[1].split('-')[1]
        if doc != last_doc:  # Are we switching to a new set of documents
            #print(len(doc_hash))
            if len(doc_hash) != 0:
                good = check_subsitutions(doc_hash, last_doc)
                if not good:
                    bad_docs.add(last_doc)
                    print(str(last_doc) + " was not consistent")
                if len(doc_hash) != 4:
                    bad_docs.add(last_doc)
                    print(str(last_doc) + " did not have all 4 subtypes")
                    print_error_table(doc_hash, last_doc)
                else:
                    #print(str(last_doc) + " was consistent")
                    good_docs.add(last_doc)
                doc_hash = {}
        last_doc = doc
        doc_hash[subtype] = count

print(str(len(bad_docs)) + " bad documents below:")
print(bad_docs)
print(str(len(good_docs)) + " good documents below:")
print(good_docs)
